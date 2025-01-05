from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from config import Config
from utils.middleware import validate_json, paginate_data, filter_and_sort_data ,handle_errors ,prevent_duplicates # Middleware
from utils.database import products_db

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Swagger UI setup
SWAGGER_URL = "/swagger"
API_URL = "/static/openapi.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Products Service API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Product schema validation
product_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "price": {"type": "number"},
        "category": {"type": "string"},
        "stock": {"type": "integer"}
    },
    "required": ["name", "description", "price", "category", "stock"]
}

@app.route('/static/openapi.yaml')
def get_openapi_yaml():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "openapi.yaml", mimetype="text/yaml")

@app.route('/api/products', methods=['GET'])
@paginate_data
@filter_and_sort_data
def get_products():
    """Retrieve all products"""
    return jsonify(products_db), 200

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """Retrieve a single product by ID"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if product:
        return jsonify(product), 200
    return jsonify({"message": "Product not found"}), 404

@app.route('/api/products', methods=['POST'])
@validate_json(product_schema)
@prevent_duplicates  # ✅ Prevent Duplicates
@handle_errors  # ✅ Handle Errors
  # ✅ Apply Rate Limiting
def add_product():
    """Add a new product"""
    data = request.json
    new_product = {
        "id": f"prod-{len(products_db) + 1}",
        "name": data["name"],
        "description": data["description"],
        "price": data["price"],
        "category": data["category"],
        "stock": data["stock"]
    }
    products_db.append(new_product)

    with open("mock_database.json", "w") as file:
        json.dump({"products": products_db}, file, indent=4)

    return jsonify(new_product), 201

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(Config.API_PORT))
