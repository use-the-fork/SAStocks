from unittest.mock import patch

import pytest

from polygon_client import PolygonClient, BASE_URL


@pytest.fixture
def polygon_client():
    return PolygonClient(api_key="test_api_key")


@patch("requests.get")
def test_get_ticker_details(mock_get, polygon_client):
    # Arrange
    # Mock response for /v3/reference/tickers/{ticker}
    mock_response_valid = {
        "request_id": "31d59dda-80e5-4721-8496-d0d32a654afe",
        "results": {
            "active": True,
            "address": {
                "address1": "One Apple Park Way",
                "city": "Cupertino",
                "postal_code": "95014",
                "state": "CA",
            },
            "branding": {
                "icon_url": "https://api.polygon.io/v1/reference/company-branding/d3d3LmFwcGxlLmNvbQ/images/2022-01-10_icon.png",
                "logo_url": "https://api.polygon.io/v1/reference/company-branding/d3d3LmFwcGxlLmNvbQ/images/2022-01-10_logo.svg",
            },
            "cik": "0000320193",
            "composite_figi": "BBG000B9XRY4",
            "currency_name": "usd",
            "description": "Apple designs a wide variety of consumer electronic devices, including smartphones (iPhone), tablets (iPad), PCs (Mac), smartwatches (Apple Watch), AirPods, and TV boxes (Apple TV), among others. The iPhone makes up the majority of Apple's total revenue. In addition, Apple offers its customers a variety of services such as Apple Music, iCloud, Apple Care, Apple TV+, Apple Arcade, Apple Card, and Apple Pay, among others. Apple's products run internally developed software and semiconductors, and the firm is well known for its integration of hardware, software and services. Apple's products are distributed online as well as through company-owned stores and third-party retailers. The company generates roughly 40% of its revenue from the Americas, with the remainder earned internationally.",
            "homepage_url": "https://www.apple.com",
            "list_date": "1980-12-12",
            "locale": "us",
            "market": "stocks",
            "market_cap": 2771126040150,
            "name": "Apple Inc.",
            "phone_number": "(408) 996-1010",
            "primary_exchange": "XNAS",
            "round_lot": 100,
            "share_class_figi": "BBG001S5N8V8",
            "share_class_shares_outstanding": 16406400000,
            "sic_code": "3571",
            "sic_description": "ELECTRONIC COMPUTERS",
            "ticker": "AAPL",
            "ticker_root": "AAPL",
            "total_employees": 154000,
            "type": "CS",
            "weighted_shares_outstanding": 16334371000,
        },
        "status": "OK",
    }
    mock_response_invalid = {"status": "ERROR", "error": "Invalid ticker symbol"}
    mock_get.return_value.json.side_effect = [
        mock_response_valid,  # First call with a valid ticker
        mock_response_invalid,  # Second call with an invalid ticker
    ]

    # Act and Assert for valid ticker
    response_valid = polygon_client.get_ticker_details("AAPL")
    assert response_valid == mock_response_valid
    mock_get.assert_called_with(
        f"{BASE_URL}/v3/reference/tickers/AAPL?&apiKey={polygon_client.api_key}"
    )

    # Act and Assert for invalid ticker
    with pytest.raises(ValueError) as context:
        polygon_client.get_ticker_details("INVALID_TICKER")
    assert "Invalid ticker symbol" in str(context.value)


@patch("requests.get")
def test_get_news(mock_get, polygon_client):
    # Mock response for /v2/reference/news with filters
    mock_response = {
        "status": "OK",
        "results": [
            {
                "title": "Market Update",
                "article_url": "https://example.com/market-update",
                "author": "Jane Doe",
                "description": "Daily market update and analysis.",
                "published_utc": "2021-04-26T02:33:17Z",
                "image_url": "https://example.com/images/market.jpg",
                "publisher": {
                    "name": "Example News",
                },
                "tickers": ["AAPL", "MSFT"],
            }
        ],
    }

    mock_get.return_value.json.return_value = mock_response
    response = polygon_client.get_news(
        "AAPL",
        published_utc="2021-03-30T00:00:00Z",
        order="ascending",
        limit=5,
        sort="published_utc",
    )
    # Assertions to verify the correctness of the response
    mock_get.assert_called_once_with(
        f"{BASE_URL}/v2/reference/news",
        params={
            "apiKey": "test_api_key",
            "ticker": "AAPL",
            "published_utc.gte": "2021-03-30T00:00:00Z",
            "order": "ascending",
            "limit": 5,
            "sort": "published_utc",
        },
    )
    assert response == mock_response
    assert response == mock_response


@patch("requests.get")
def test_get_open_close(mock_get, polygon_client):
    # Arrange
    # Mock response for /v1/open-close/{ticker}/{date}
    mock_response_valid = {
        "status": "OK",
        "results": {
            "afterHours": 322.1,
            "close": 325.12,
            "from": "2023-01-09",
            "high": 326.2,
            "low": 322.3,
            "open": 324.66,
            "preMarket": 324.5,
            "status": "OK",
            "symbol": "AAPL",
            "volume": 26122646,
        },
    }
    mock_response_invalid_ticker = {
        "status": "ERROR",
        "error": "Invalid ticker symbol",
    }
    mock_response_invalid_date = {"status": "ERROR", "error": "Invalid date format"}
    mock_get.return_value.json.side_effect = [
        mock_response_valid,  # First call with valid inputs
        mock_response_invalid_ticker,  # Second call with an invalid ticker
        mock_response_invalid_date,  # Third call with an invalid date
    ]

    # Act and Assert for valid inputs
    response_valid = polygon_client.get_open_close("AAPL", "2023-01-09")
    assert response_valid == mock_response_valid
    mock_get.assert_called_with(
        f"{BASE_URL}/v1/open-close/AAPL/2023-01-09?adjusted=true&apiKey={polygon_client.api_key}"
    )

    # Act and Assert for invalid ticker
    with pytest.raises(ValueError) as context_ticker:
        polygon_client.get_open_close("INVALID_TICKER", "2023-01-09")
    assert "Invalid ticker symbol" in str(context_ticker.value)

    # Act and Assert for invalid date
    with pytest.raises(ValueError) as context_date:
        polygon_client.get_open_close("AAPL", "invalid-date")
    assert "Invalid date format" in str(context_date.value)
