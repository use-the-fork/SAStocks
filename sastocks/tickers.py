from sastocks.config import DatabaseSession
from sastocks.logger import logger
from sastocks.models import Ticker
from sastocks.polygon_client import PolygonClient

polygon_client = PolygonClient()


def add_ticker(symbol: str):
    """Adds a new ticker to the database if it's a valid symbol.

    Args:
        symbol (str): The stock symbol to add.

    Returns:
        None
    """
    try:
        # Use PolygonClient to get ticker details
        ticker_details = polygon_client.get_ticker_details(symbol)
        if ticker_details.get("status") != "OK":
            logger.error(f"Invalid symbol or error retrieving details: {symbol}")
            return
    except ValueError as e:
        logger.error(f"Error validating symbol: {symbol}. Exception: {e}")
        return

    with DatabaseSession() as session:
        try:
            # Check if the symbol already exists in the database
            existing_ticker = session.query(Ticker).filter_by(symbol=symbol).first()
            if existing_ticker:
                logger.info(f"Symbol '{symbol}' already exists in the database.")
                return

            # Extract the name and other details from PolygonClient ticker details
            name = ticker_details["results"].get("name", "Unknown")
            new_ticker = Ticker(symbol=symbol, name=name)
            session.add(new_ticker)
            session.commit()
            logger.info(f"Ticker '{symbol}' added successfully.")
        except Exception as e:
            logger.error(f"Failed to add ticker '{symbol}'. Exception: {e}")
            session.rollback()
