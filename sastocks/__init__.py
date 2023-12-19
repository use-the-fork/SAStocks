import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Now you can use os.environ to access environment variables
polygon_key = os.environ.get("POLYGON_API_KEY")
if polygon_key is None:
    raise ValueError("POLYGON_API_KEY is not set in the .env file.")
__version__ = "0.1.0"