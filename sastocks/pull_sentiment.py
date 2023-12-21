import os

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from sqlalchemy.orm import sessionmaker

from sastocks.config import database_engine
from sastocks.logger import logger
from sastocks.models import NewsArticle

# Create a session factory using the database engine from the config module
DatabaseSession = sessionmaker(bind=database_engine)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class Sentiment(BaseModel):
    sentiment: str = Field(
        description="`YES` if good news, `NO` if bad news, or `UNKNOWN` if uncertain in the first line"
    )
    reason: str = Field(description="one short and concise sentence")


parser = PydanticOutputParser(pydantic_object=Sentiment)

temperature = 0.0
model = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY, model_name="gpt-4", temperature=temperature
)

sentiment_template = """# INSTRUCTIONS: 
    Forget all your previous instructions. You are a financial expert with stock recommendation experience. 
    Answer “YES” if good news, “NO” if bad news, or “UNKNOWN” if uncertain in the first line. 
    Then elaborate with one short and concise sentence. 

# CONSTRAINTS:
- You MUST respond in the response format (below).
- Do not add anything before or after the response only use the below response format.
- Do NOT make up anything.

# RESPONSE FORMAT:
{format_instructions}

# USER INPUT
Is this headline good or bad for the stock price of {company_name} in the {term} term?
Headline: {headline}"""


prompt = PromptTemplate(
    template=sentiment_template,
    input_variables=["company_name", "term", "headline"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

sentiment_analyzer = prompt | model | parser


def do_news_sentiment_analysis():
    logger.info("Starting news sentiment analysis...")
    with DatabaseSession() as session:
        # Retrieve all news articles with an empty gpt_sentiment value
        articles = (
            session.query(NewsArticle).filter(NewsArticle.gpt_sentiment == None).all()
        )

        # Process each article
        for article in articles:
            result = sentiment_analyzer.invoke(
                {
                    "headline": article.title,
                    # Retrieve the company name using the ticker associated with the article
                    "company_name": article.ticker.name,
                    "term": "short",
                }
            )
            # Update the article with the sentiment analysis results
            article.gpt_sentiment = result.sentiment
            article.gpt_response = result.reason
            session.commit()

            pass

    logger.info("Finished news sentiment analysis.")
