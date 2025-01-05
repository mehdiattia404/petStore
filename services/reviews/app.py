from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import sys
import os
import datetime
from config import Config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.database import reviews_db, products_db, users_db
from utils.middleware import validate_json, paginate_data, filter_and_sort_data ,handle_errors ,prevent_duplicates,admin_required # Middleware

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Swagger UI setup
SWAGGER_URL = "/swagger"
API_URL = "/static/openapi.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Reviews Service API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/openapi.yaml')
def get_openapi_yaml():
    """Serve OpenAPI YAML file"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "openapi.yaml", mimetype="text/yaml")

# ✅ Review schema validation
review_schema = {
    "type": "object",
    "properties": {
        "user_id": {"type": "string"},
        "product_id": {"type": "string"},
        "rating": {"type": "integer", "minimum": 1, "maximum": 5},
        "comment": {"type": "string"}
    },
    "required": ["user_id", "product_id", "rating"]
}

@app.route('/api/reviews', methods=['GET'])
@paginate_data  # ✅ Apply pagination
@filter_and_sort_data  # ✅ Apply filtering & sorting
def get_reviews():
    """Retrieve all reviews"""
    return jsonify(reviews_db), 200

@app.route('/api/reviews/<review_id>', methods=['GET'])
def get_review_by_id(review_id):
    """Retrieve a single review by ID"""
    review = next((r for r in reviews_db if r["id"] == review_id), None)
    if review:
        return jsonify(review), 200
    return jsonify({"error": "Review not found"}), 404

@app.route('/api/reviews/product/<product_id>', methods=['GET'])
@paginate_data
@filter_and_sort_data
def get_reviews_by_product(product_id):
    """Retrieve reviews for a specific product"""
    product_reviews = [r for r in reviews_db if r["product_id"] == product_id]
    return jsonify(product_reviews), 200

@app.route('/api/reviews', methods=['POST'])
@validate_json(review_schema)  # ✅ Validate request body
@prevent_duplicates  # ✅ Prevent Duplicates
@handle_errors  # ✅ Handle Errors
  # ✅ Apply Rate Limiting
def add_review():
    """Add a review for a product"""
    data = request.json

    user = next((u for u in users_db if u["id"] == data["user_id"]), None)
    product = next((p for p in products_db if p["id"] == data["product_id"]), None)

    if not user:
        return jsonify({"error": "User not found"}), 404
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # ✅ Create review with `createdAt` timestamp
    new_review = {
        "id": f"review-{len(reviews_db) + 1}",
        "user_id": data["user_id"],
        "product_id": data["product_id"],
        "rating": data["rating"],
        "comment": data.get("comment", ""),
        "createdAt": datetime.datetime.utcnow().isoformat()  # ✅ Added review timestamp
    }
    
    reviews_db.append(new_review)

    # ✅ Save review to mock database
    with open("mock_database.json", "w") as file:
        json.dump({"reviews": reviews_db}, file, indent=4)

    return jsonify(new_review), 201

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(Config.API_PORT))
