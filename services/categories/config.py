import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    API_PORT = os.getenv("API_PORT", 5000)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
