"""Database initialization for SAStocks.

This module sets up the SQLAlchemy engine and session factory for interacting with the database.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Constants for the database file and path
DATABASE_FILE_NAME = "sastocks_db.sqlite"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "../../", DATABASE_FILE_NAME)

# Construct the database URL for SQLite
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)

# Create a scoped session factory using the engine
DatabaseSession = sessionmaker(bind=engine)
# Session = scoped_session(session_factory)

# Create a session object from the session factory
# session = Session()
