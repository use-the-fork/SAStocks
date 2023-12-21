# Get required components
import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sastocks.console import console
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
    tickers = Ticker.query().all()
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

    # Check if the article already exists in the database
    existing_article = NewsArticle.query().filter_by(url=article_url).first()
    if existing_article:
        console.info(f"Article '{title}' already exists in database.")
        return

    # Create a new NewsArticle instance
    NewsArticle().create(
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
    console.info(f"Article '{title}' added successfully to the database.")


def process_api_response(api_response, ticker: Ticker):
    if api_response.get("status") != "OK":
        console.error(
            f"Error: {api_response.get('status')} - {api_response.get('error')}"
        )
        return
    for result in api_response["results"]:
        date = datetime.strptime(result["published_utc"], "%Y-%m-%dT%H:%M:%SZ").date()
        title = result.get("title", "")
        description = result.get("description", "")
        article_url = result.get("article_url", "")
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


def pull_news(date_range: Tuple[str, str] = None):
    """Pull news for all tickers and save them to the database."""
    # Ensure the POLYGON_API_KEY is available
    if not polygon_key:
        raise EnvironmentError("POLYGON_API_KEY environment variable not found.")

    # Instantiate PolygonClient
    polygon_client = PolygonClient(api_key=polygon_key)

    # Parse the start and end dates from the date_range parameter
    start_date = datetime.strptime(date_range[0], "%Y-%m-%d")
    end_date = datetime.strptime(date_range[1], "%Y-%m-%d")

    # Iterate over each day within the date range
    current_date = start_date
    while current_date <= end_date:
        timestamp = current_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Load the tickers
        tickers = load_tickers()

        # Download news articles for all tickers
        console.info(
            f"Importing and Filtering News from Polygon.io for all tickers for date {current_date.date()}"
        )
        for i, ticker in enumerate(tickers, start=1):
            console.info(f"Importing news for ticker #{i}: {ticker.symbol}")

            # Execute the request, get the response and process it
            try:
                api_response = polygon_client.get_news(
                    ticker.symbol, published_utc=timestamp
                )
                process_api_response(api_response, ticker)
            except Exception as e:
                console.error(
                    f"An error occurred while processing {ticker.symbol}: {e}"
                )
                continue

            console.info(f"Finished importing and filtering news for {ticker.symbol}")

        # Move to the next day
        current_date += timedelta(days=1)

    console.info("News Capture Completed - Database Prepared")
