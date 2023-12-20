import os
import re
from typing import Optional

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
        published_utc_operator: str = "gte",
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
        allowed_operators = {"gt", "gte", "lt", "lte"}
        if published_utc_operator not in allowed_operators:
            raise ValueError(
                f"Invalid published_utc_operator: {published_utc_operator}. Allowed values are {allowed_operators}."
            )
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

    def get_rsi(
        self,
        ticker: str,
        timespan: str = "day",
        adjusted: bool = True,
        window: int = 14,
        series_type: str = "close",
        order: str = "desc",
        timestamp: Optional[str] = None,
        expand_underlying: bool = False,
        limit: int = 10,
    ) -> dict:
        """
        Get the Relative Strength Index (RSI) for a given ticker.

        Args:
            ticker (str): The ticker symbol to get RSI for.
            timespan (str): The timespan for the RSI data.
            adjusted (bool): Whether to adjust the data.
            window (int): The window size for RSI calculation.
            series_type (str): The type of price series to use.
            order (str): The order of the results.
            timestamp (Optional[str]): The timestamp to query by. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
            expand_underlying (bool): Whether to include the aggregates used to calculate this indicator in the response.
            limit (int): Limit the number of results returned, default is 10 and max is 5000.

        Returns:
            dict: The API response containing RSI data.
        """
        params = {
            "timespan": timespan,
            "adjusted": str(adjusted).lower(),
            "window": window,
            "series_type": series_type,
            "order": order,
            "apiKey": self.api_key,
            "expand_underlying": str(expand_underlying).lower(),
            "limit": limit,
        }
        if timestamp:
            if re.match(r"^\d{4}-\d{2}-\d{2}$", timestamp) or re.match(
                r"^\d+$", timestamp
            ):
                params["timestamp"] = timestamp
            else:
                raise ValueError(
                    "Invalid timestamp format. Must be YYYY-MM-DD or a millisecond timestamp."
                )
        url = f"{BASE_URL}/v1/indicators/rsi/{ticker.upper()}"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_macd(
        self,
        ticker: str,
        timespan: str = "day",
        adjusted: bool = True,
        short_window: int = 12,
        long_window: int = 26,
        signal_window: int = 9,
        series_type: str = "close",
        order: str = "desc",
        timestamp: Optional[str] = None,
        expand_underlying: bool = False,
        limit: int = 10,
    ) -> dict:
        """
        Get the Moving Average Convergence Divergence (MACD) for a given ticker.

        Args:
            ticker (str): The ticker symbol to get MACD for.
            timespan (str): The timespan for the MACD data.
            adjusted (bool): Whether to adjust the data.
            short_window (int): The short window size for MACD calculation.
            long_window (int): The long window size for MACD calculation.
            signal_window (int): The signal window size for MACD calculation.
            series_type (str): The type of price series to use.
            order (str): The order of the results.
            timestamp (Optional[str]): The timestamp to query by. Either a date with the format YYYY-MM-DD or a millisecond timestamp.
            expand_underlying (bool): Whether to include the aggregates used to calculate this indicator in the response.
            limit (int): Limit the number of results returned, default is 10 and max is 5000.

        Returns:
            dict: The API response containing MACD data.
        """
        params = {
            "timespan": timespan,
            "adjusted": str(adjusted).lower(),
            "short_window": short_window,
            "long_window": long_window,
            "signal_window": signal_window,
            "series_type": series_type,
            "order": order,
            "apiKey": self.api_key,
            "expand_underlying": str(expand_underlying).lower(),
            "limit": limit,
        }
        if timestamp:
            if re.match(r"^\d{4}-\d{2}-\d{2}$", timestamp) or re.match(
                r"^\d+$", timestamp
            ):
                params["timestamp"] = timestamp
            else:
                raise ValueError(
                    "Invalid timestamp format. Must be YYYY-MM-DD or a millisecond timestamp."
                )
        url = f"{BASE_URL}/v1/indicators/macd/{ticker.upper()}"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
