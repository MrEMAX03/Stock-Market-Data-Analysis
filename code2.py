import requests
import json
import sys
from datetime import date
import statistics

def download_data(ticker: str) -> dict:
    """Fetch historical stock data from Nasdaq API."""
    ticker = ticker.upper()
    today = date.today()
    start = str(today.replace(year=today.year - 5))
    base_url = "https://api.nasdaq.com"
    path = f"/api/quote/{ticker}/historical?assetclass=stocks&fromdate={start}&limit=9999"
    url = base_url + path
    headers = {"User-Agent": "Mozilla/5.0"}  # Some APIs require a user-agent
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {ticker}: {e}")
        return {}

def process_data(data: dict) -> dict:
    """Extract and compute stock statistics."""
    try:
        prices = [float(row['close'].strip('$').replace(',', '')) for entry in data.get("data", {}).get("tradesTable", {}).get("rows", [])]
        if not prices:
            return {}
        return {
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / len(prices),
            "median": statistics.median(prices)
        }
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error processing data: {e}")
        return {}

def main():
    """Main function to fetch and process stock data."""
    if len(sys.argv) < 2:
        print("Usage: python stocks.py <TICKER1> <TICKER2> ...")
        sys.exit(1)
    
    tickers = sys.argv[1:]
    results = []
    
    for ticker in tickers:
        data = download_data(ticker)
        stats = process_data(data)
        if stats:
            stats["ticker"] = ticker
            results.append(stats)
    
    if results:
        try:
            with open("stocks.json", "w") as f:
                json.dump(results, f, indent=4)
            print("Data saved to stocks.json")
        except IOError as e:
            print(f"Error writing to file: {e}")
    else:
        print("No valid stock data available.")

if __name__ == "__main__":
    main()
