from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import sys
import os
from datetime import datetime

from config import Config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.database import orders_db, cart_db, users_db, products_db
from utils.middleware import validate_json, paginate_data, filter_and_sort_data ,handle_errors ,prevent_duplicates,admin_required # Middleware

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Swagger UI setup
SWAGGER_URL = "/swagger"
API_URL = "/static/openapi.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Orders Service API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/openapi.yaml')
def get_openapi_yaml():
    """Serve OpenAPI YAML file"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "openapi.yaml", mimetype="text/yaml")

# ✅ Order schema validation
order_schema = {
    "type": "object",
    "properties": {
        "user_id": {"type": "string"},
        "cart_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "quantity": {"type": "integer", "minimum": 1}
                },
                "required": ["product_id", "quantity"]
            },
            "minItems": 1
        },
        "status": {"type": "string", "enum": ["pending", "confirmed", "shipped", "delivered"]}
    },
    "required": ["user_id", "cart_items", "status"]
}

@app.route('/api/orders', methods=['GET'])
@paginate_data  # ✅ Apply pagination
@filter_and_sort_data  # ✅ Apply filtering & sorting
def get_orders():
    """Retrieve all orders"""
    return jsonify(orders_db), 200

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order_by_id(order_id):
    """Retrieve a single order by ID"""
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if order:
        return jsonify(order), 200
    return jsonify({"error": "Order not found"}), 404

@app.route('/api/orders', methods=['POST'])
@validate_json(order_schema)  # ✅ Validate request body
@prevent_duplicates  # ✅ Prevent Duplicates
@handle_errors  # ✅ Handle Errors
  # ✅ Apply Rate Limiting
def place_order():
    """Place a new order from the cart"""
    data = request.json

    # ✅ Check if user exists
    user = next((u for u in users_db if u["id"] == data["user_id"]), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # ✅ Check if the user's cart exists
    user_cart = next((cart for cart in cart_db if cart["userId"] == data["user_id"]), None)
    if not user_cart or len(user_cart["items"]) == 0:
        return jsonify({"error": "Cart is empty"}), 400

    # ✅ Calculate total price dynamically & update cart items with product prices
    total_price = 0
    updated_cart_items = []

    for item in data["cart_items"]:
        product = next((p for p in products_db if p["id"] == item["product_id"]), None)
        if not product:
            return jsonify({"error": f"Product with ID {item['product_id']} not found"}), 404

        if item["quantity"] > product["stock"]:
            return jsonify({"error": f"Not enough stock available for {product['name']}"}), 400

        # ✅ Store only productId and quantity, but fetch price dynamically
        cart_item = {
            "productId": item["product_id"],
            "quantity": item["quantity"],
            "price": product["price"]

        }
        updated_cart_items.append(cart_item)

        total_price += product["price"] * item["quantity"]

    # ✅ Create the order with `createdAt` timestamp
    new_order = {
        "id": f"order-{len(orders_db) + 1}",
        "user_id": data["user_id"],
        "cart_items": updated_cart_items,  # ✅ Updated with product references
        "total_price": total_price,  # ✅ Automatically calculated
        "status": "pending",
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }

    orders_db.append(new_order)

    # ✅ Save order to mock database
    with open("mock_database.json", "w") as file:
        json.dump({"orders": orders_db}, file, indent=4)

    return jsonify(new_order), 201

@app.route('/api/orders/<order_id>', methods=['PUT'])
@admin_required  # ✅ Only Admins Can Update Orders
@handle_errors  # ✅ Handle Errors
  # ✅ Apply Rate Limiting
def update_order_status(order_id):
    """Update order status"""
    data = request.json
    order = next((o for o in orders_db if o["id"] == order_id), None)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    valid_transitions = {
        "pending": ["confirmed"],
        "confirmed": ["shipped"],
        "shipped": ["delivered"],
        "delivered": []  # No further status updates allowed
    }

    current_status = order["status"]
    new_status = data.get("status")

    if new_status not in valid_transitions[current_status]:
        return jsonify({"error": f"Invalid status transition from {current_status} to {new_status}"}), 400

    # ✅ Update order status
    order["status"] = new_status

    # ✅ If confirmed, update inventory in `products_db`
    if new_status == "confirmed":
        for item in order["cart_items"]:
            product = next((p for p in products_db if p["id"] == item["productId"]), None)
            if product:
                product["stock"] -= item["quantity"]

    # ✅ Save changes
    with open("mock_database.json", "w") as file:
        json.dump({"orders": orders_db, "products": products_db}, file, indent=4)

    return jsonify(order), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(Config.API_PORT))
