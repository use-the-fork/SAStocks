from sastocks.console import console
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
            console.error(f"Invalid symbol or error retrieving details: {symbol}")
            return
    except ValueError as e:
        console.error(f"Error validating symbol: {symbol}. Exception: {e}")
        return

    try:
        # Check if the symbol already exists in the database
        existing_ticker = Ticker.query().filter_by(symbol=symbol).first()
        if existing_ticker:
            console.info(f"Symbol '{symbol}' already exists in the database.")
            return

        # Extract the name and other details from PolygonClient ticker details
        name = ticker_details["results"].get("name", "Unknown")
        Ticker().create(symbol=symbol, name=name)
        console.info(f"Ticker '{symbol}' added successfully.")
    except Exception as e:
        console.error(f"Failed to add ticker '{symbol}'. Exception: {e}")
