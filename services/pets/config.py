import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_PORT = os.getenv("PETS_SERVICE_PORT", 5000) 
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
