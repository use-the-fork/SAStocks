from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from sastocks.database import DatabaseSession, engine


class Base(DeclarativeBase):
    @classmethod
    def create(cls, **kw):
        with DatabaseSession() as s:
            obj = cls(**kw)
            s.add(obj)
            s.commit()
            s.refresh(obj)
            return obj

    @classmethod
    def update(cls, id, **kwargs):
        with DatabaseSession() as s:
            obj = s.query(cls).get(id)
            for key, value in kwargs.items():
                setattr(obj, key, value)
            s.commit()
            s.refresh(obj)
            return obj

    @classmethod
    def remove(cls, id):
        with DatabaseSession() as s:
            obj = s.query(cls).get(id)
            s.delete(obj)
            s.commit()

    @classmethod
    def query(cls):
        return DatabaseSession().query(cls)


class Ticker(Base):
    __tablename__ = "ticker"

    id: Mapped[int] = Column(Integer, primary_key=True)
    symbol: Mapped[str] = Column(String(10))
    name: Mapped[str] = mapped_column(String(255))

    news_articles = relationship("NewsArticle", back_populates="ticker")
    sentiment_scores = relationship("SentimentScore", back_populates="ticker")


class NewsArticle(Base):
    __tablename__ = "news_article"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String)
    keywords: Mapped[str] = mapped_column(String)
    publisher: Mapped[str] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    amp_url: Mapped[str] = mapped_column(String)
    vader_sentiment: Mapped[str] = Column(String)
    gpt_sentiment: Mapped[str] = Column(String)
    gpt_response: Mapped[str] = Column(String)

    ticker_id = Column(Integer, ForeignKey("ticker.id"))
    ticker: Mapped["Ticker"] = relationship("Ticker", back_populates="news_articles")

    def __repr__(self) -> str:
        return (
            f"<NewsArticle(title={self.title}, date={self.date}, author={self.author})>"
        )


class SentimentScore(Base):
    __tablename__ = "sentiment_scores"

    id: Mapped[int] = Column(Integer, primary_key=True)
    date: Mapped[str] = Column(String)

    historical_price_high: Mapped[float] = Column(Float)
    historical_price_low: Mapped[float] = Column(Float)
    historical_price_open: Mapped[float] = Column(Float)
    historical_price_close: Mapped[float] = Column(Float)
    historical_price_after_hours: Mapped[float] = Column(Float)
    historical_price_volume: Mapped[float] = Column(Float)

    aggregated_score: Mapped[float] = Column(Float)
    rsi: Mapped[float] = Column(Float)
    macd: Mapped[float] = Column(Float)

    ticker_id = Column(Integer, ForeignKey("ticker.id"))
    ticker: Mapped["Ticker"] = relationship("Ticker", back_populates="sentiment_scores")

    def __repr__(self) -> str:
        return f"<SentimentScore(ticker={self.ticker}, date={self.date})>"


Base.metadata.create_all(bind=engine)
