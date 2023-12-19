import os
from typing import Optional

from pydantic.dataclasses import dataclass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sastocks.logger import logger
from sastocks.models import Base

# Form Recognizer credentials
ENDPOINT = os.environ.get("DPM_ENDPOINT")
API_KEY = os.environ.get("DPM_API_KEY")

# Get the directory the script is running from
APP_ROOT = os.getcwd()

# Path to SQLite database
database_path = os.path.join(APP_ROOT, "sastocks_db.sqlite")

# Correct the database URL format for SQLite
database_url = f"sqlite:///{database_path}"

database_engine = create_engine(database_url)
DatabaseSession = sessionmaker(bind=database_engine)


def init_config(log=False):
    """Initialize the configuration file if it doesn't exist."""

    # Create all tables in the engine
    Base.metadata.create_all(database_engine)

    if log:
        logger.info(f"Database initialized at {database_path}")

    return database_engine


@dataclass()
class RunSettings:
    # Name of the module (python file) used in the run command
    module_name: Optional[str] = None
    target: Optional[str] = None
    headless: bool = False
    watch: bool = False
    no_cache: bool = False
    debug: bool = False
    ci: bool = False


@dataclass()
class SAStocksConfig:
    # Directory where the project is located
    root = APP_ROOT
    run: RunSettings


def load_config():
    """Load the configuration from the config file."""
    engine = init_config()

    config = SAStocksConfig(run=RunSettings())

    return config


config = load_config()
