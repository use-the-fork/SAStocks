from unittest.mock import patch, MagicMock
import pytest
from sastocks.tickers import add_ticker
from sastocks.models import Ticker
from sastocks.polygon_client import PolygonClient

@pytest.fixture
def mock_session():
    with patch("sastocks.tickers.DatabaseSession") as mock:
        yield mock

@pytest.fixture
def mock_polygon_client():
    with patch("sastocks.tickers.PolygonClient") as mock:
        yield mock

def test_add_valid_ticker(mock_session, mock_polygon_client):
    # Arrange
    mock_polygon_client_instance = mock_polygon_client.return_value
    mock_polygon_client_instance.get_ticker_details.return_value = {
        "status": "OK",
        "results": {"name": "Apple Inc."}
    }
    mock_db_session = mock_session.return_value.__enter__.return_value
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    add_ticker("AAPL")

    # Assert
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_add_duplicate_ticker(mock_session, mock_polygon_client):
    # Arrange
    mock_polygon_client_instance = mock_polygon_client.return_value
    mock_polygon_client_instance.get_ticker_details.return_value = {
        "status": "OK",
        "results": {"name": "Apple Inc."}
    }
    mock_db_session = mock_session.return_value.__enter__.return_value
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = Ticker(id=1, symbol="AAPL", name="Apple Inc.")

    # Act
    add_ticker("AAPL")

    # Assert
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()

def test_add_invalid_ticker(mock_session, mock_polygon_client):
    # Arrange
    mock_polygon_client_instance = mock_polygon_client.return_value
    mock_polygon_client_instance.get_ticker_details.return_value = {
        "status": "ERROR",
        "error": "Invalid ticker symbol"
    }

    # Act
    add_ticker("INVALID")

    # Assert
    mock_session.return_value.__enter__.return_value.add.assert_not_called()
    mock_session.return_value.__enter__.return_value.commit.assert_not_called()