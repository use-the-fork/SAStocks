import os
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from sastocks.config import database_engine
from sastocks.logger import logger
from sastocks.models import SentimentScore
from sastocks.models import Ticker
from sastocks.polygon_client import PolygonClient

# Create a session factory using the database engine from the config module
DatabaseSession = sessionmaker(bind=database_engine)

# Load the Polygon API key from the environment variable
API_KEY = os.environ.get("POLYGON_API_KEY")

# Initialize the PolygonClient with the API key
polygon_client = PolygonClient(api_key=API_KEY)


def pull_financials(date=None):
    logger.info("Starting to pull financial data...")
    # Use the provided date or default to today's date if no date is provided
    date = date or datetime.now().strftime("%Y-%m-%d")

    # Establish a session with the database
    with DatabaseSession() as session:
        # Retrieve all tickers from the database
        tickers = session.query(Ticker).all()

        # Process each ticker
        for ticker in tickers:
            try:
                # Retrieve financial data using PolygonClient
                rsi_data = polygon_client.get_rsi(ticker.symbol)
                macd_data = polygon_client.get_macd(ticker.symbol)
                open_close_data = polygon_client.get_open_close(ticker.symbol, date)

                # Combine the data
                combined_data = {
                    "date": datetime.strptime(date, "%Y-%m-%d").date(),
                    "ticker_id": ticker.id,
                    "rsi": rsi_data.get("results", {})
                    .get("values", [])[0]
                    .get("value"),
                    "macd": macd_data.get("results", {})
                    .get("values", [])[0]
                    .get("value"),
                    "historical_price_high": open_close_data.get("high"),
                    "historical_price_low": open_close_data.get("low"),
                    "historical_price_open": open_close_data.get("open"),
                    "historical_price_close": open_close_data.get("close"),
                    "historical_price_after_hours": open_close_data.get("afterHours"),
                    "historical_price_volume": open_close_data.get("volume"),
                }

                # Check if there is already a record for this ticker and date
                existing_score = (
                    session.query(SentimentScore)
                    .filter_by(ticker_id=ticker.id, date=combined_data["date"])
                    .first()
                )
                if existing_score:
                    # Update the existing record with the new data
                    for key, value in combined_data.items():
                        setattr(existing_score, key, value)
                    logger.info(
                        f"Updated financial data for ticker: {ticker.symbol} on date: {combined_data['date']}"
                    )
                else:
                    # Create a new SentimentScore object with the combined data
                    sentiment_score = SentimentScore(**combined_data)
                    # Add the new object to the session
                    session.add(sentiment_score)
                    logger.info(
                        f"Added new financial data for ticker: {ticker.symbol} on date: {combined_data['date']}"
                    )
                # Commit the changes to the database
                session.commit()
                logger.info(
                    f"Successfully pulled financial data for ticker: {ticker.symbol}"
                )
            except Exception as e:
                logger.error(f"An error occurred while pulling financial data: {e}")

    logger.info("Finished pulling financial data.")
