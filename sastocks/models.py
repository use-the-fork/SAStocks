from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Ticker(Base):
    __tablename__ = "ticker"

    id: Mapped[int] = Column(Integer, primary_key=True)
    symbol: Mapped[str] = Column(String(10))
    name: Mapped[str] = mapped_column(String(255))

    news_articles = relationship("NewsArticle", back_populates="ticker")


class NewsArticle(Base):
    __tablename__ = "news_article"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1000))
    url: Mapped[str] = mapped_column(String(500))
    author: Mapped[str] = mapped_column(String(100))
    keywords: Mapped[str] = mapped_column(String(500))
    publisher: Mapped[str] = mapped_column(String(100))
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    amp_url: Mapped[str] = mapped_column(String(500))

    ticker_id = Column(Integer, ForeignKey("ticker.id"))
    ticker: Mapped["Ticker"] = relationship("Ticker", back_populates="news_articles")

    def __repr__(self) -> str:
        return f"<NewsArticle(title={self.title}, date={self.date}, author={self.author})>"
