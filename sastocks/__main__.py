import os

from dotenv import load_dotenv

from sastocks.logger import logger

env_found = load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


if env_found:
    logger.info("Loaded .env file")
