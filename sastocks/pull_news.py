# Get required components
import os
from datetime import datetime, timedelta
from typing import List, Optional

from sastocks.config import DatabaseSession
from sastocks.logger import logger
from sastocks.models import NewsArticle
from sastocks.models import Ticker
from sastocks.polygon_client import PolygonClient

# Load API keys from CSV
polygon_key = os.environ.get("POLYGON_API_KEY")


def load_tickers() -> List[Ticker]:
    """Load all tickers from the database using the Ticker model.

    Returns:
        List[Ticker]: A list of Ticker objects.
    """
    with DatabaseSession() as session:
        tickers = session.query(Ticker).all()
        return tickers


def save_news_to_db(
    date: datetime,
    ticker: Ticker,
    title: str,
    description: str,
    article_url: str,
    author: str,
    keywords: str,
    publisher: str,
    image_url: Optional[str] = None,
    amp_url: Optional[str] = None,
):
    """Save news article to the database using the NewsArticle model.

    Args:
        date (str): The publication date of the article.
        ticker (Ticker): The Ticker object associated with the article.
        title (str): The title of the article.
        description (str): The description of the article.
        article_url (str): The URL of the article.
        author (str): The author of the article.
        keywords (str): The keywords associated with the article.
        publisher (str): The publisher of the article.
        image_url (str): The URL of the article's image.
        amp_url (str): The AMP URL of the article.
    """
    with DatabaseSession() as session:
        # Check if the article already exists in the database
        existing_article = session.query(NewsArticle).filter_by(url=article_url).first()
        if existing_article:
            logger.info(f"Article '{title}' already exists in database.")
            return

        # Create a new NewsArticle instance
        new_article = NewsArticle(
            date=date,
            title=title,
            description=description,
            url=article_url,
            author=author,
            keywords=keywords,
            publisher=publisher,
            ticker_id=ticker.id,
            image_url=image_url,
            amp_url=amp_url,
        )
        session.add(new_article)
        session.commit()
        logger.info(f"Article '{title}' added successfully to the database.")


def process_api_response(api_response, ticker: Ticker):
    if api_response.get("status") != "OK":
        logger.error(
            f"Error: {api_response.get('status')} - {api_response.get('error')}"
        )
        return
    for result in api_response["results"]:
        date = datetime.strptime(result["published_utc"], "%Y-%m-%dT%H:%M:%SZ").date()
        title = result["title"]
        description = result["description"]
        article_url = result["article_url"]
        author = result.get(
            "author", "Unknown"
        )  # Use a default value if author is not provided
        keywords = ", ".join(
            result.get("keywords", [])
        )  # Join keywords into a string, use empty list if not provided
        publisher = result["publisher"].get(
            "name", "Unknown"
        )  # Use a default value if publisher name is not provided
        image_url = result.get(
            "image_url", ""
        )  # Use an empty string if image_url is not provided
        amp_url = result.get(
            "amp_url", ""
        )  # Use an empty string if amp_url is not provided
        save_news_to_db(
            date,
            ticker,
            title,
            description,
            article_url,
            author,
            keywords,
            publisher,
            image_url,
            amp_url,
        )


def pull_news(
    timestamp: str = (datetime.utcnow() - timedelta(days=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ),
):
    """Pull news for all tickers and save them to the database."""
    # Ensure the POLYGON_API_KEY is available
    if not polygon_key:
        raise EnvironmentError("POLYGON_API_KEY environment variable not found.")

    # Instantiate PolygonClient
    polygon_client = PolygonClient(api_key=polygon_key)

    # Use provided timestamp or set to yesterday's date if not provided
    if not timestamp:
        timestamp = (datetime.utcnow() - timedelta(days=1)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    # Load the tickers
    tickers = load_tickers()

    # Download news articles for all tickers
    logger.info("Importing and Filtering News from Polygon.io for all tickers")
    for i, ticker in enumerate(tickers, start=1):
        logger.info(f"Importing news for ticker #{i}: {ticker.symbol}")

        # Execute the request, get the response and process it
        try:
            api_response = polygon_client.get_news(
                ticker.symbol, published_utc=timestamp
            )
            process_api_response(api_response, ticker)
        except Exception as e:
            logger.error(f"An error occurred while processing {ticker.symbol}: {e}")
            continue

        logger.info(f"Finished importing and filtering news for {ticker.symbol}")

    logger.info("News Capture Completed - Database Prepared")
