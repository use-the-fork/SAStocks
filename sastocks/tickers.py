import yfinance as yf

from sastocks.config import DatabaseSession
from sastocks.logger import logger
from sastocks.models import Ticker


def add_ticker(symbol: str):
    """Adds a new ticker to the database if it's a valid symbol.

    Args:
        symbol (str): The stock symbol to add.

    Returns:
        None
    """
    yf_symbol = yf.Ticker(symbol)

    try:
        # Validate the symbol by checking if it has a regular market price
        if "longName" not in yf_symbol.info:
            logger.error(f"Invalid symbol: {symbol}")
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

            # Extract the name from yfinance symbol info
            name = (
                yf_symbol.info.get("longName")
                or yf_symbol.info.get("shortName")
                or "Unknown"
            )
            new_ticker = Ticker(symbol=symbol, name=name)
            session.add(new_ticker)
            session.commit()
            logger.info(f"Ticker '{symbol}' added successfully.")
        except Exception as e:
            logger.error(f"Failed to add ticker '{symbol}'. Exception: {e}")
            session.rollback()
