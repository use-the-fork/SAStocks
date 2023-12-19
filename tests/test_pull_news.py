from unittest.mock import patch

import pytest

from sastocks.models import Ticker
from sastocks.pull_news import pull_news


@pytest.fixture
def mock_session():
    with patch("sastocks.pull_news.DatabaseSession") as mock:
        yield mock


@pytest.fixture
def mock_polygon_client():
    with patch("sastocks.pull_news.PolygonClient.get_news") as mock:
        yield mock


def test_pull_news_success(mock_session, mock_polygon_client):
    # Arrange
    mock_client_instance = mock_polygon_client
    mock_client_instance.return_value = {
        "status": "OK",
        "results": [
            {
                "published_utc": "2023-12-19T16:42:32Z",
                "title": "Company News",
                "description": "Latest company news.",
                "article_url": "https://example.com/news",
                "author": "Reporter",
                "keywords": ["finance", "stocks"],
                "publisher": {"name": "Example News"},
                "image_url": "https://example.com/image.jpg",
                "amp_url": "https://example.com/amp",
            }
        ],
    }

    ticker = Ticker(id=1, symbol="AAPL", name="Apple Inc.")
    mock_session.return_value.__enter__.return_value.query.return_value.filter_by.return_value.first.return_value = (
        ticker
    )

    # Act
    pull_news()


def test_pull_news_api_error(mock_session, mock_polygon_client):
    # Arrange
    mock_client_instance = mock_polygon_client
    mock_client_instance.return_value = {
        "status": "ERROR",
        "error": "An error occurred",
    }

    ticker = Ticker(id=1, symbol="AAPL", name="Apple Inc.")
    mock_session.return_value.__enter__.return_value.query.return_value.filter_by.return_value.first.return_value = (
        ticker
    )

    # Act
    pull_news()

    # Assert
    mock_session.return_value.__enter__.return_value.add.assert_not_called()


def test_pull_news_no_tickers(mock_session, mock_polygon_client):
    # Arrange
    mock_session.return_value.__enter__.return_value.query.return_value.all.return_value = (
        []
    )

    # Act
    pull_news()

    # Assert
    mock_session.return_value.__enter__.return_value.add.assert_not_called()
    mock_session.return_value.__enter__.return_value.add.assert_not_called()
