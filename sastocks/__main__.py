import os

from dotenv import load_dotenv

from sastocks.console import console

env_found = load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


if env_found:
    console.info("Loaded .env file")
