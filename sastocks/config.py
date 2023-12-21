import os

# Form Recognizer credentials
ENDPOINT = os.environ.get("DPM_ENDPOINT")
API_KEY = os.environ.get("DPM_API_KEY")

# Get the directory the script is running from
APP_ROOT = os.getcwd()


# Load variables from .env
basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, ".env"))

# Reset data after each run
CLEANUP_DATA = False
