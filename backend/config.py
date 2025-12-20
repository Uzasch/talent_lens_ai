import os
from dotenv import load_dotenv

load_dotenv()

# Get the directory where this config file lives (backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'app.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
