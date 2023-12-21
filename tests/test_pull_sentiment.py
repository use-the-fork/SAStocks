from unittest.mock import patch

import pytest

from sastocks.pull_sentiment import do_news_sentiment_analysis


@pytest.fixture
def mock_session():
    with patch("sastocks.pull_sentiment.DatabaseSession") as mock:
        yield mock


@pytest.fixture
def mock_sentiment_analyzer():
    with patch("sastocks.pull_sentiment.sentiment_analyzer") as mock:
        yield mock


def test_do_news_sentiment_analysis(mock_session, mock_sentiment_analyzer):
    # Arrange
    # mock_db_session = mock_session.return_value.__enter__.return_value
    # mock_article = NewsArticle(
    #     id=1,
    #     title="Test Article",
    #     description="This is a test article for sentiment analysis.",
    #     url="http://example.com/news/test-article",
    #     author="Test Author",
    #     keywords="test, article",
    #     publisher="Test Publisher",
    #     ticker=Ticker(id=1, symbol="TEST", name="Test Inc."),
    #     gpt_sentiment=None
    # )
    # mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_article]
    # mock_sentiment_analyzer.invoke.return_value = {
    #     "sentiment": "Positive",
    #     "reason": "The test article is positive."
    # }

    # Act
    do_news_sentiment_analysis()

    # Assert
    # mock_db_session.query.assert_called_with(NewsArticle)
    # mock_db_session.query.return_value.filter.assert_called_with(NewsArticle.gpt_sentiment == None)
    # mock_sentiment_analyzer.invoke.assert_called_once()
    # assert mock_article.gpt_sentiment == "Positive", "The gpt_sentiment should be updated to 'Positive'"
