import os
from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy.orm import sessionmaker

from sastocks.console import console
from sastocks.database import engine
from sastocks.models import SentimentScore, Ticker
from sastocks.polygon_client import PolygonClient

# Create a session factory using the database engine from the config module
DatabaseSession = sessionmaker(bind=engine)

# Load the Polygon API key from the environment variable
API_KEY = os.environ.get("POLYGON_API_KEY")

# Initialize the PolygonClient with the API key
polygon_client = PolygonClient(api_key=API_KEY)


def pull_financials(date_range: Tuple[str, str] = None):
    """Pull financial data for all tickers and save them to the database."""
    console.info("Starting to pull financial data...")
    # Parse the start and end dates from the date_range parameter
    start_date = datetime.strptime(date_range[0], "%Y-%m-%d")
    end_date = datetime.strptime(date_range[1], "%Y-%m-%d")

    # Iterate over each day within the date range
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")

        # Establish a session with the database

        # Retrieve all tickers from the database
        tickers = Ticker.query().all()

        # Process each ticker
        for ticker in tickers:
            # Retrieve financial data using PolygonClient
            rsi_data = polygon_client.get_rsi(ticker.symbol)
            macd_data = polygon_client.get_macd(ticker.symbol)
            open_close_data = polygon_client.get_open_close(ticker.symbol, date_str)

            # Combine the data
            combined_data = {
                "date": current_date.date(),
                "ticker_id": ticker.id,
                "rsi": rsi_data.get("results", {}).get("values", [])[0].get("value"),
                "macd": macd_data.get("results", {}).get("values", [])[0].get("value"),
                "historical_price_high": open_close_data.get("high"),
                "historical_price_low": open_close_data.get("low"),
                "historical_price_open": open_close_data.get("open"),
                "historical_price_close": open_close_data.get("close"),
                "historical_price_after_hours": open_close_data.get("afterHours"),
                "historical_price_volume": open_close_data.get("volume"),
            }

            # Check if there is already a record for this ticker and date
            existing_score = (
                SentimentScore.query()
                .filter_by(ticker_id=ticker.id, date=combined_data["date"])
                .first()
            )
            if existing_score:
                # Update the existing record with the new data
                existing_score.update(existing_score.id, kwargs=combined_data.items())
                console.info(
                    f"Updated financial data for ticker: {ticker.symbol} on date: {combined_data['date']}"
                )
            else:
                # Create a new SentimentScore object with the combined data
                SentimentScore().create(**combined_data)
                console.info(
                    f"Added new financial data for ticker: {ticker.symbol} on date: {combined_data['date']}"
                )

            console.info(
                f"Successfully pulled financial data for ticker: {ticker.symbol}"
            )

        # Move to the next day
        current_date += timedelta(days=1)

    console.info("Finished pulling financial data.")
