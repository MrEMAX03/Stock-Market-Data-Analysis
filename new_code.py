"""
Module 3 Assignment - Stock Market Data Analysis

Author: Emanuele Bossi
Student ID: #2641192
Description:    This program downloads data related to some ticker given by the user from NASDAQ and
                computes some statistical measures.
Class: DS 244
Date: 02-10-2025
"""

import requests
from datetime import date
import json
import sys
from typing import List, Dict, Union


BASE_URL = "https://api.nasdaq.com"

def extract_close(ticker_data: List) -> List:
    """
    Extract from the stock data of a given ticker the closing price.

    Args:
        ticker_data (list): List of dictionaries containing historical stock data for a ticker.

    Returns:
        (list): A list of closing prices as floats.
    """
    return [float(row['close'].strip('$').replace(',', '')) for row in ticker_data]

def download_data(ticker: str) -> List:
    """
    Fetch historical stock data for the given ticker from Nasdaq API.

    Args:
        ticker (str): ticker symbol (e.g., AAPL, MSFT, GOOGL, AMZN, TSLA)

    Returns:
        (list or dict): A list of closing prices or an error message.
    """
    ticker = ticker.upper()
    today = date.today()
    start = str(today.replace(year=today.year - 1))  # Fetching last 1 year of data
    path = f"/api/quote/{ticker}/historical?assetclass=stocks&fromdate={start}&limit=9999"
    
    url = BASE_URL + path

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error if request fails
        data = response.json()

        # Extract rCode
        rcode = data.get("status", {}).get("rCode", None)
        if rcode != 200:
            return {"error": f"Failed to fetch data for {ticker}. rCode: {rcode}"}

        # Extract closing prices safely
        try:
            trades_table = data.get('data', {}).get('tradesTable', {})
            rows = trades_table.get('rows', [])
            closing = extract_close(rows) if rows else []
            return closing
        except (KeyError, TypeError):
            return {"error": "Invalid data format for tradesTable"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching data for {ticker}: {str(e)}"}
    
def compute_median(ls: List) -> float:
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

def data_processing(tickers: List[str])->List[Dict]:
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

    results = []

    for ticker in tickers:
        closing = download_data(ticker)  # Get closing prices list

        if isinstance(closing, dict) and "error" in closing:
            print(f"Skipping {ticker}: {closing['error']}")
            continue

        if not closing:
            print(f"No data available for {ticker}. Skipping.")
            continue

        ticker_stats = {
            "min": min(closing),
            "max": max(closing),
            "avg": sum(closing) / len(closing),
            "median": compute_median(closing),
            "ticker": ticker
        }

        results.append(ticker_stats)

    return results

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

def process_tickers(tickers: List[str]) -> List[Dict]:
    """
    Download and process stock data for the given tickers.

    Args:
        tickers (List[str]): A list of stock ticker symbols.

    Returns:
        List[Dict]: Processed stock data.
    """
    return data_processing(tickers)

# Get ticker symbols from command-line arguments
tickers = sys.argv[1:]

if tickers:
    stocks_data = process_tickers(tickers)
    write_to_json(stocks_data, 'stocks_NEW.json')
else:
    print("Please provide at least one ticker symbol.")