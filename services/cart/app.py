from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import sys
import os
from config import Config
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.database import cart_db, products_db, users_db
from utils.middleware import validate_json, paginate_data, filter_and_sort_data ,handle_errors ,prevent_duplicates # Middleware

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Swagger UI setup
SWAGGER_URL = "/swagger"
API_URL = "/static/openapi.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Cart Service API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/openapi.yaml')
def get_openapi_yaml():
    """Serve OpenAPI YAML file"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "openapi.yaml", mimetype="text/yaml")

# ✅ Cart schema for validation
cart_item_schema = {
    "type": "object",
    "properties": {
        "user_id": {"type": "string"},
        "product_id": {"type": "string"},
        "quantity": {"type": "integer", "minimum": 1}
    },
    "required": ["user_id", "product_id", "quantity"]
}
@app.route('/api/cart', methods=['GET'])
@filter_and_sort_data  # ✅ Apply filtering & sorting
def get_cart():
    """Retrieve all items in the cart for a specific user with pagination"""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # ✅ Find user's cart
    user_cart = next((cart for cart in cart_db if cart["userId"] == user_id), None)

    if not user_cart:
        return jsonify({"user_id": user_id, "items": [], "totalAmount": 0, "createdAt": None}), 200

    # ✅ Extract items before pagination
    items = user_cart["items"]

    # ✅ Apply pagination manually
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    start = (page - 1) * limit
    end = start + limit

    paginated_items = items[start:end]

    return jsonify({
        "user_id": user_cart["userId"],
        "items": paginated_items,  # ✅ Paginated items
        "totalAmount": user_cart["totalAmount"],
        "createdAt": user_cart["createdAt"],
        "pagination": {  # ✅ Pagination metadata
            "page": page,
            "limit": limit,
            "total": len(items)
        }
    }), 200

@app.route('/api/cart/products', methods=['GET'])
def get_available_products():
    """Retrieve available products for dropdown selection"""
    product_options = [{"id": p["id"], "name": p["name"], "stock": p["stock"]} for p in products_db]
    return jsonify(product_options), 200


@app.route('/api/cart', methods=['POST'])
@validate_json(cart_item_schema)  # ✅ Validate request body
@prevent_duplicates  # ✅ Prevent Duplicates
@handle_errors  # ✅ Handle Errors
def add_to_cart():
    """Add a product to the cart with correct structure"""
    data = request.json

    # ✅ Check if user exists
    user = next((u for u in users_db if u["id"] == data["user_id"]), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # ✅ Check product availability
    product = next((p for p in products_db if p["id"] == data["product_id"]), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # ✅ Check stock availability
    if data["quantity"] > product["stock"]:
        return jsonify({"error": "Not enough stock available"}), 400

    # ✅ Retrieve or create the user's cart
    user_cart = next((cart for cart in cart_db if cart["userId"] == data["user_id"]), None)

    if not user_cart:
        user_cart = {
            "id": f"cart-{len(cart_db) + 1}",
            "userId": data["user_id"],
            "items": [],
            "totalAmount": 0,
            "createdAt": datetime.utcnow().isoformat() + "Z"
        }
        cart_db.append(user_cart)

    # ✅ Check if the product is already in the cart
    existing_item = next((item for item in user_cart["items"] if item["productId"] == data["product_id"]), None)

    if existing_item:
        # Update quantity
        existing_item["quantity"] += data["quantity"]
    else:
        # Add new item to the cart
        user_cart["items"].append({
            "productId": data["product_id"],
            "quantity": data["quantity"],
            "price": product["price"]
        })

    # ✅ Recalculate the total amount
    user_cart["totalAmount"] = sum(item["price"] * item["quantity"] for item in user_cart["items"])

    # ✅ Update stock in the product database
    product["stock"] -= data["quantity"]

    # ✅ Save updated cart and products back to the mock database
    with open("mock_database.json", "w") as file:
        json.dump({"cart": cart_db, "products": products_db, "users": users_db}, file, indent=4)

    return jsonify(user_cart), 201


@app.route('/api/cart/items', methods=['GET'])
def get_cart_items():
    """Retrieve available cart items for dropdown selection"""
    cart_options = [{"id": item["id"], "product_name": item["product_name"], "user_id": item["user_id"]} for item in cart_db]
    return jsonify(cart_options), 200


@app.route('/api/cart/<cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    """Remove an item from the cart for a specific user"""
    global cart_db
    cart_item = next((item for item in cart_db if item["id"] == cart_id), None)

    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404

    # ✅ Restore stock when removing from cart
    product = next((p for p in products_db if p["id"] == cart_item["productId"]), None)
    if product:
        product["stock"] += cart_item["quantity"]

    # ✅ Remove the item from the cart
    cart_db = [item for item in cart_db if item["id"] != cart_id]

    # ✅ Save updated cart & products to mock database
    with open("mock_database.json", "w") as file:
        json.dump({"cart": cart_db, "products": products_db}, file, indent=4)

    return jsonify({"message": "Item removed from cart"}), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(Config.API_PORT))
