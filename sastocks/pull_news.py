# Get required components
import os
from typing import List

import requests

from sastocks.config import DatabaseSession
from sastocks.logger import logger
from sastocks.models import Ticker

# Load API keys from CSV
polygon_key = os.environ.get("POLYGON_API_KEY")

# Polygon.io API setup
polygon_url = (
    "https://api.polygon.io/v2/reference/news?ticker=AA&published_utc.gte=2021-03-30T00:00:00Z&limit.max=10000&sort=published_utc&apiKey="
    + polygon_key
)


def load_tickers() -> List[Ticker]:
    """Load all tickers from the database using the Ticker model.

    Returns:
        List[Ticker]: A list of Ticker objects.
    """
    with DatabaseSession() as session:
        tickers = session.query(Ticker).all()
        return tickers


from sastocks.models import NewsArticle


def save_news_to_db(
    date: str,
    ticker: Ticker,
    title: str,
    description: str,
    article_url: str,
    author: str,
    keywords: str,
    publisher: str,
    image_url: str,
    amp_url: str,
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
        date = result["published_utc"]
        title = result["title"]
        description = result["description"]
        article_url = result["article_url"]
        author = result["author"]
        keywords = ", ".join(result["keywords"])
        publisher = result["publisher"]["name"]
        image_url = result["image_url"]
        amp_url = result["amp_url"]
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


def pull_news():
    """Pull news for all tickers and save them to the database."""

    # Load the tickers
    tickers = load_tickers()

    # Download news articles for all tickers
    logger.info("Importing and Filtering News from Polygon.io for all tickers")
    for i, ticker in enumerate(tickers, start=1):
        logger.info(f"Importing news for ticker #{i}: {ticker.symbol}")

        # Execute the request, get the response and process it
        try:
            api_response = requests.get(polygon_url.format(ticker=ticker.symbol)).json()
            process_api_response(api_response, ticker)
        except Exception as e:
            logger.error(f"An error occurred while processing {ticker.symbol}: {e}")
            continue

        logger.info(f"Finished importing and filtering news for {ticker.symbol}")

    logger.info("News Capture Completed - Database Prepared")
