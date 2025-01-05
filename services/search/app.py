from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import sys
import os
from config import Config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.database import products_db, categories_db
from utils.middleware import paginate_data, filter_and_sort_data  # Import middleware

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Swagger UI setup
SWAGGER_URL = "/swagger"
API_URL = "/static/openapi.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Search Service API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/openapi.yaml')
def get_openapi_yaml():
    """Serve OpenAPI YAML file"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "openapi.yaml", mimetype="text/yaml")

@app.route('/api/search', methods=['GET'])
@paginate_data  # ✅ Apply pagination
@filter_and_sort_data  # ✅ Apply sorting
def search_products():
    """
    Search for products by keyword (q) and category
    """
    query = request.args.get("q", "").lower()

    # Filter products by name or category match
    results = [
        product for product in products_db
        if query in product["name"].lower() or query in product["category"].lower()
    ]

    return jsonify(results), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(Config.API_PORT))
