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
    
def extract_close(ticker_data: list) -> list:
    """
    Extract from the stock data of a given ticker the closing price.

    Args:
        ticker_data (list): List of dictionaries containing historical stock data for a ticker.

    Returns:
        (list): A list of closing prices as floats.
    """
    return [float(row['close'].strip('$').replace(',', '')) for row in ticker_data]

def compute_median(ls: list) -> float:
    """
    Compute the median of a list.
    
    Args:
        ls (list): the list we want to compute the median.
    
    Returns:
        (float): the median of the list given.
    """
    # Sort the list
    sorted_ls = sorted(ls)
    
    # Find the number of elements
    n = len(sorted_ls)
    
    # If the list has an odd number of elements, return the middle one
    if n % 2 == 1:
        return sorted_ls[n // 2]
    else:
        # If the list has an even number of elements, return the average of the two middle ones
        middle_left = sorted_ls[n // 2 - 1]
        middle_right = sorted_ls[n // 2]
        return (middle_left + middle_right) / 2

def data_processing2(data: dict, tickers: list[str])->list[dict]:
    """
    This function completes the core part of this assignment: data processing. Using helper functions,
    it extract closing prices from the raw data, and compute several statistical measures (e.g., 
    min, max, average, and median) of the data.
    
    Args:
        data (dict): the dictionary containing all the data.
        tickers (list[str]): the list containing all the tickers we want to analyze.
    
    Returns:
        (list[dict]): list of dictionary containing the various statistical measures for each ticker.
    """

    ls = []
    for ticker in tickers:
        ticker_dict = {}

        # Extract just closing prices
        closing = extract_close(data[ticker]['data']['tradesTable']['rows'])

        # Compute min
        ticker_dict['min'] = min(closing)

        # Compute max
        ticker_dict['max'] = max(closing)

        # Compute avg
        ticker_dict['avg'] = sum(closing)/ data[ticker]['data']['totalRecords']

        # Compute medium
        ticker_dict['medium'] = compute_median(closing)

        # Save symbol (e.g., AAPL)
        ticker_dict['ticker'] = data[ticker]['data']['symbol']

        ls.append(ticker_dict)

    return ls

def data_processing(data: dict, tickers: list[str]) -> list[dict]:
    """
    This function completes the core part of this assignment: data processing. Using helper functions,
    it extract closing prices from the raw data, and compute several statistical measures (e.g., 
    min, max, average, and median) of the data.
    
    Args:
        data (dict): the dictionary containing all the data.
        tickers (list[str]): the list containing all the tickers we want to analyze.
    
    Returns:
        (list[dict]): list of dictionary containing the various statistical measures for each ticker.
    """
    ls = []
    for ticker in tickers:
        if data[ticker] is None:  # Handle invalid tickers
            print(f"Skipping {ticker} due to missing data.")
            continue

        try:
            closing = extract_close(data[ticker]['data']['tradesTable']['rows'])

            ticker_dict = {
                'min': min(closing),
                'max': max(closing),
                'avg': sum(closing) / len(closing),  # Fix division by total records
                'median': compute_median(closing),  # Fix spelling from "medium" to "median"
                'ticker': ticker
            }
            ls.append(ticker_dict)
        except KeyError:
            print(f"Error processing data for {ticker}. Skipping.")
            continue  # Skip invalid tickers safely

    return ls


def write_to_json(stocks_data: list[dict], file_path: str) -> None:
    """
    This function transforms a list of dictionaries to a .json file and save it.
    
    Args:
        stocks_data (list[dict]): the list of dictionary we want to convert to .json format.
        file_path (str): the name of the file path where we want to save the .json file.
    """

    try:
        with open(file_path, 'w') as json_file:
            json.dump(stocks_data, json_file, indent=4)
        print(f"Data has been successfully written to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


# I had no idea on how to satisfy the following requirement:
# "Allow your program to be called with ticker symbols like so: python stocks.py AAPL MSFT GOOGL AMZN TSLA"
# For this reason, I've used ChatGPT to produce the code below - however, I created the docstring for the function

# Function to process the tickers and prepare the stock data
def process_tickers(tickers: list) -> list:
    """
    This function allows to process the data (download and "actual" statistical processing) for each ticker inserted by the user.
    
    Args:
        stocks_data (list[dict]): the list of dictionary we want to convert to .json format.
        file_path (str): the name of the file path where we want to save the .json file.
    """
    stocks_data = {}

    for ticker in tickers:
        raw_data = download_data(ticker)
        stocks_data[ticker] = raw_data  # Store the raw data in the dictionary

    # Process the data after fetching it
    processed_data = data_processing(stocks_data, tickers)

    return processed_data


# Get ticker symbols from command-line arguments (excluding the script name)
tickers = sys.argv[1:]

if tickers:
    # Process the tickers and prepare stock data
    stocks_data = process_tickers(tickers)

    # Write the processed stock data to a JSON file
    write_to_json(stocks_data, 'stocks.json')
else:
    print("Please provide at least one ticker symbol.")