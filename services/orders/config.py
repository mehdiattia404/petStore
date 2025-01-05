import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Orders Service"""

    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_APP = os.getenv("FLASK_APP", "app.py")
    FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    FLASK_RUN_PORT = int(os.getenv("FLASK_RUN_PORT", 5000))
    API_PORT = int(os.getenv("API_PORT", 5000))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mahdi")
    MOCK_DB_PATH = os.getenv("MOCK_DB_PATH", "../mock_database.json")
