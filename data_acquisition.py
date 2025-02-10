import requests
from datetime import date
import json
import sys

BASE_URL = "https://api.nasdaq.com"

def download_data(ticker: str) -> dict:
    """
    Fetch historical stock data for the given ticker from Nasdaq API.

    Args:
        ticker (str): ticker symbol (e.g., AAPL, MSFT, GOOGL, AMZN, TSLA)

    Returns:
        (dict): a dictionary containing stock prices over a specified period (e.g., 5 years)
    """
    ticker = ticker.upper()
    today = date.today()
    start = str(today.replace(year=today.year - 5))  # To get data from last five years onwards
    path = f"/api/quote/{ticker}/historical?assetclass=stocks&fromdate={start}&limit=9999"
    
    url = BASE_URL + path

    # I had some issues running the code without the following 3 lines.
    # I did some researches and found that some APIs require a User-Agent to allow access.
    # For this reason, I asked ChatGPT to create the three lines below.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Will raise an error if status code is 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching data for {ticker}: {str(e)}"}
    
# Sample usage
print(download_data("AAPL"))