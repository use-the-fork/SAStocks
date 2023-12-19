import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Now you can use os.environ to access environment variables
polygon_key = os.environ.get("POLYGON_API_KEY")
if not polygon_key:
    raise EnvironmentError("POLYGON_API_KEY environment variable not found.")
__version__ = "0.1.0"