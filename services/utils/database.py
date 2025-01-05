import json
import os

# Define path to mock database
mock_db_path = os.path.join(os.path.dirname(__file__), "../mock_database.json")

# Load mock database
if os.path.exists(mock_db_path):
    with open(mock_db_path, "r") as file:
        data = json.load(file)
        products_db = data.get("products", [])
        categories_db = data.get("categories", [])
        users_db = data.get("users", [])
        cart_db = data.get("cart", [])
        orders_db = data.get("orders", [])
        reviews_db = data.get("reviews", [])
        pets_db = data.get("pets", [])
else:
    products_db = []
    categories_db = []
    users_db = []
    cart_db = []
    orders_db = []
    reviews_db = []
    pets_db = []
