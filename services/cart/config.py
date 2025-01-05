import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_PORT = os.getenv("CART_SERVICE_PORT", 5000)
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
