from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import sys
import os
from config import Config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.database import categories_db
from utils.middleware import validate_json, paginate_data, filter_and_sort_data  # ✅ Import utilities

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Swagger UI setup
SWAGGER_URL = "/swagger"
API_URL = "/static/openapi.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Categories Service API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/openapi.yaml')
def get_openapi_yaml():
    """Serve OpenAPI YAML file"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "openapi.yaml", mimetype="text/yaml")

# ✅ Category schema for validation
category_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"}
    },
    "required": ["name", "description"]
}

@app.route('/api/categories', methods=['GET'])
@paginate_data  # ✅ Pagination
@filter_and_sort_data  # ✅ Filtering and Sorting
def get_categories():
    """Retrieve all categories with pagination, filtering, and sorting"""
    return jsonify(categories_db), 200

@app.route('/api/categories/<category_id>', methods=['GET'])
def get_category_by_id(category_id):
    """Retrieve a single category by ID"""
    category = next((c for c in categories_db if c["id"] == category_id), None)
    if category:
        return jsonify(category), 200
    return jsonify({"message": "Category not found"}), 404

@app.route('/api/categories', methods=['POST'])
@validate_json(category_schema)  # ✅ Validate request body
def add_category():
    """Add a new category"""
    data = request.json
    new_category = {
        "id": f"cat-{len(categories_db) + 1}",
        "name": data["name"],
        "description": data["description"]
    }
    categories_db.append(new_category)

    with open("mock_database.json", "w") as file:
        json.dump({"categories": categories_db}, file, indent=4)

    return jsonify(new_category), 201

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(Config.API_PORT))
