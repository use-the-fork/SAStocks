import os

import re
import requests

# Load the Polygon API key from the environment variable
API_KEY = os.environ.get("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"


class PolygonClient:
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key

    def get_ticker_details(self, ticker: str) -> dict:
        """
        Get details for a single ticker.

        Args:
            ticker (str): The ticker symbol to get details for.

        Returns:
            dict: A dictionary containing the details of the ticker.
        """
        # Validate and sanitize ticker input
        if not isinstance(ticker, str) or not ticker.isalnum():
            raise ValueError("Invalid ticker symbol. Ticker must be alphanumeric.")
        url = f"{BASE_URL}/v3/reference/tickers/{ticker.upper()}?&apiKey={self.api_key}"
        response = requests.get(url)
        return response.json()

    def get_news(
        self,
        ticker: str,
        published_utc: str = None,
        published_utc_operator: str = 'gte',
        order: str = None,
        limit: int = 10,
        sort: str = None,
    ) -> dict:
        """Get news for a single ticker with optional filters.

        Args:
            ticker (str): The ticker symbol to get news for.
            published_utc (str): The UTC date and time to filter news by.
            published_utc_operator (str): The operator to use for the published_utc filter. 
                                          Allowed values are 'gt', 'gte', 'lt', 'lte'.
            order (str): The order of the results.
            limit (int): The number of results to return.
            sort (str): The field to sort by.

        Returns:
            dict: The API response containing news articles.
        """
        # Validate and sanitize inputs
        allowed_operators = {'gt', 'gte', 'lt', 'lte'}
        if published_utc_operator not in allowed_operators:
            raise ValueError(f"Invalid published_utc_operator: {published_utc_operator}. Allowed values are {allowed_operators}.")
        if not isinstance(ticker, str) or not ticker.isalnum():
            raise ValueError("Invalid ticker symbol. Ticker must be alphanumeric.")

        params = {
            "apiKey": self.api_key,
            "ticker": ticker.upper(),
            "order": order,
            "limit": limit,
            "sort": sort,
        }
        # Add published_utc filter if provided
        if published_utc:
            params[f"published_utc.{published_utc_operator}"] = published_utc

        # Filter out None values
        params = {k: v for k, v in params.items() if v is not None}
        url = f"{BASE_URL}/v2/reference/news"
        response = requests.get(url, params=params)
        return response.json()

    def get_open_close(self, ticker: str, date: str) -> dict:
        """
        Get the open and close prices for a single ticker on a given date.

        Args:
            ticker (str): The ticker symbol to get open and close prices for.
            date (str): The date for which to get the prices in YYYY-MM-DD format.

        Returns:
            dict: A dictionary containing the open and close prices along with other relevant information.
        """
        # Validate and sanitize ticker input
        if not isinstance(ticker, str) or not ticker.isalnum():
            raise ValueError("Invalid ticker symbol. Ticker must be alphanumeric.")
        # Validate date format (YYYY-MM-DD)
        if not isinstance(date, str) or not re.match(r"\d{4}-\d{2}-\d{2}", date):
            raise ValueError("Invalid date format. Date must be in YYYY-MM-DD format.")
        url = f"{BASE_URL}/v1/open-close/{ticker.upper()}/{date}?adjusted=true&apiKey={self.api_key}"
        response = requests.get(url)
        return response.json()
