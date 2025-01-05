import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_PORT = os.getenv("REVIEWS_SERVICE_PORT", 5000)
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
