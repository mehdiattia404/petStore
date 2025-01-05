import os

class Config:
    """Configuration for API Gateway"""
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000
    SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
    
    # Microservices Mapping with API prefixes
    SERVICES = {
        "auth": "http://127.0.0.1:5001",
        "products": "http://127.0.0.1:5002",
        "categories": "http://127.0.0.1:5003",
        "search": "http://127.0.0.1:5004",
        "cart": "http://127.0.0.1:5005",
        "orders": "http://127.0.0.1:5006",
    }
