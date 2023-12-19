import os
import unittest

# Set POLYGON_API_KEY for testing
os.environ["POLYGON_API_KEY"] = "test_api_key"
from sastocks.pull_news import polygon_url
from unittest.mock import patch, MagicMock


class TestPullNews(unittest.TestCase):
    # Additional test cases can be added here to cover different scenarios
    @patch("sastocks.pull_news.save_news_to_db")
    def test_process_api_response(self, mock_save_news_to_db):
        # Arrange
        api_response = {
            "status": "OK",
            "results": [
                {
                    "published_utc": "2023-04-01T12:00:00Z",
                    "title": "Test Article 1",
                    "description": "This is a test description for article 1.",
                    "article_url": "http://example.com/news/test-article-1",
                    "author": "Test Author 1",
                    "keywords": ["test", "news", "article1"],
                    "publisher": {"name": "Test Publisher 1"},
                    "image_url": "http://example.com/news/test-image-1.jpg",
                    "amp_url": "http://example.com/news/test-article-1/amp",
                },
                {
                    "published_utc": "2023-04-02T12:00:00Z",
                    "title": "Test Article 2",
                    "description": "This is a test description for article 2.",
                    "article_url": "http://example.com/news/test-article-2",
                    "author": "Test Author 2",
                    "keywords": ["test", "news", "article2"],
                    "publisher": {"name": "Test Publisher 2"},
                    "image_url": "http://example.com/news/test-image-2.jpg",
                    "amp_url": "http://example.com/news/test-article-2/amp",
                },
            ],
        }
        mock_ticker = MagicMock()
        mock_ticker.id = 1

        # Act
        from sastocks.pull_news import process_api_response

        process_api_response(api_response, mock_ticker)

        # Assert
        assert mock_save_news_to_db.call_count == 2
        expected_calls = [
            unittest.mock.call(
                "2023-04-01T12:00:00Z",
                mock_ticker,
                "Test Article 1",
                "This is a test description for article 1.",
                "http://example.com/news/test-article-1",
                "Test Author 1",
                "test, news, article1",
                "Test Publisher 1",
                "http://example.com/news/test-image-1.jpg",
                "http://example.com/news/test-article-1/amp",
            ),
            unittest.mock.call(
                "2023-04-02T12:00:00Z",
                mock_ticker,
                "Test Article 2",
                "This is a test description for article 2.",
                "http://example.com/news/test-article-2",
                "Test Author 2",
                "test, news, article2",
                "Test Publisher 2",
                "http://example.com/news/test-image-2.jpg",
                "http://example.com/news/test-article-2/amp",
            ),
        ]
        mock_save_news_to_db.assert_has_calls(expected_calls, any_order=True)

    @patch("sastocks.pull_news.DatabaseSession")
    def test_save_news_to_db(self, mock_db_session):
        # Arrange
        mock_session = MagicMock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_ticker = MagicMock()
        mock_ticker.id = 1
        mock_ticker.ticker_symbol = "MSFT"
        news_data = {
            "date": "2023-04-01T12:00:00Z",
            "ticker": mock_ticker,
            "title": "Test Article",
            "description": "This is a test description.",
            "article_url": "http://example.com/news/test-article",
            "author": "Test Author",
            "keywords": "test, news",
            "publisher": "Test Publisher",
            "image_url": "http://example.com/news/test-image.jpg",
            "amp_url": "http://example.com/news/test-article/amp",
        }

        # Act
        from sastocks.pull_news import save_news_to_db

        save_news_to_db(**news_data)

        # Assert
        assert mock_session.add.called
        assert mock_session.commit.called
        added_article = mock_session.add.call_args[0][0]
        assert added_article.date == news_data["date"]
        assert added_article.ticker_id == mock_ticker.id
        assert added_article.title == news_data["title"]
        assert added_article.description == news_data["description"]
        assert added_article.url == news_data["article_url"]
        assert added_article.author == news_data["author"]
        assert added_article.keywords == news_data["keywords"]
        assert added_article.publisher == news_data["publisher"]

    @patch("sastocks.pull_news.process_api_response")
    @patch("sastocks.pull_news.requests.get")
    @patch("sastocks.pull_news.requests.get")
    def test_pull_news(self, mock_get):
        # Arrange
        mock_ticker = MagicMock()
        mock_ticker.symbol = "AAPL"
        mock_get.return_value.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "published_utc": "2023-04-01T12:00:00Z",
                    "title": "Apple News",
                    "description": "Apple releases new product.",
                    "article_url": "http://example.com/news/apple-news",
                    "author": "John Doe",
                    "keywords": ["apple", "product", "release"],
                    "publisher": {"name": "Tech News"},
                    "image_url": "http://example.com/news/apple-image.jpg",
                    "amp_url": "http://example.com/news/apple-news/amp",
                }
            ],
        }

        # Act
        from sastocks.pull_news import pull_news
        pull_news()

        # Assert
        mock_get.assert_called_once_with(
            "https://api.polygon.io/v2/reference/news?ticker=AAPL&published_utc.gte=2021-03-30T00:00:00Z&limit.max=10000&sort=published_utc&apiKey=test_api_key"
        )
        self.assertEqual(mock_save_news_to_db.call_count, 1)
        mock_save_news_to_db.assert_called_with(
            "2023-04-01T12:00:00Z",
            mock_ticker,
            "Apple News",
            "Apple releases new product.",
            "http://example.com/news/apple-news",
            "John Doe",
            "apple, product, release",
            "Tech News",
            "http://example.com/news/apple-image.jpg",
            "http://example.com/news/apple-news/amp",
        )


if __name__ == "__main__":
    unittest.main()
