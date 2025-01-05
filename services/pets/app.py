from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import sys
import os
from datetime import datetime
from config import Config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.database import pets_db, products_db, categories_db
from utils.middleware import validate_json, paginate_data, filter_and_sort_data  # Middleware

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Swagger UI setup
SWAGGER_URL = "/swagger"
API_URL = "/static/openapi.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Pets Service API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/openapi.yaml')
def get_openapi_yaml():
    """Serve OpenAPI YAML file"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "openapi.yaml", mimetype="text/yaml")

# ✅ Pet schema validation
pet_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "species": {"type": "string"},
        "breed": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
        "owner_id": {"type": "string"},
    },
    "required": ["name", "species", "breed", "age", "owner_id"]
}

@app.route('/api/pets', methods=['GET'])
@paginate_data  # ✅ Apply pagination
@filter_and_sort_data  # ✅ Apply filtering & sorting
def get_pets():
    """
    Retrieve all pets or filter by user ownership.
    """
    owner_id = request.args.get("owner_id")
    if owner_id:
        user_pets = [p for p in pets_db if p["owner_id"] == owner_id]
        return jsonify(user_pets), 200

    return jsonify(pets_db), 200

@app.route('/api/pets/<pet_id>', methods=['GET'])
def get_pet_by_id(pet_id):
    """Retrieve a single pet by ID"""
    pet = next((p for p in pets_db if p["id"] == pet_id), None)
    if pet:
        return jsonify(pet), 200
    return jsonify({"error": "Pet not found"}), 404

@app.route('/api/pets', methods=['POST'])
@validate_json(pet_schema)  # ✅ Validate request body
def add_pet():
    """Add a new pet"""
    data = request.json
    new_pet = {
        "id": f"pet-{len(pets_db) + 1}",
        "name": data["name"],
        "species": data["species"],
        "breed": data["breed"],
        "age": data["age"],
        "owner_id": data["owner_id"],
        "createdAt": datetime.utcnow().isoformat()  # ✅ Add timestamp
    }
    
    pets_db.append(new_pet)

    # ✅ Save pet to mock database
    with open("mock_database.json", "r") as file:
        db_data = json.load(file)
    db_data["pets"] = pets_db  # Update pets list

    with open("mock_database.json", "w") as file:
        json.dump(db_data, file, indent=4)

    return jsonify(new_pet), 201

@app.route('/api/pets/<pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    """Delete a pet"""
    global pets_db
    pets_db = [p for p in pets_db if p["id"] != pet_id]

    # ✅ Save updated list
    with open("mock_database.json", "r") as file:
        db_data = json.load(file)
    db_data["pets"] = pets_db

    with open("mock_database.json", "w") as file:
        json.dump(db_data, file, indent=4)

    return jsonify({"message": "Pet deleted successfully"}), 200

@app.route('/api/pets/recommendations', methods=['GET'])
def get_user_recommendations():
    """
    Retrieve recommended products based on user's pets and categories.
    """
    owner_id = request.args.get("owner_id")
    
    if not owner_id:
        return jsonify({"error": "Owner ID is required"}), 400
    
    user_pets = [p for p in pets_db if p["owner_id"] == owner_id]
    
    if not user_pets:
        return jsonify({"error": "No pets found for this user"}), 404

    recommended_products = []
    
    for pet in user_pets:
        # Find products related to pet's species
        pet_products = [p for p in products_db if pet["species"].lower() == p["animalType"].lower()]

        # Filter products to show only **food** category
        food_category_id = next((c["id"] for c in categories_db if "aliment" in c["name"].lower()), None)

        if food_category_id:
            pet_products = [p for p in pet_products if p["category"] == food_category_id]

        recommended_products.extend(pet_products)

    return jsonify({
        "owner_id": owner_id,
        "pets": user_pets,
        "recommended_products": recommended_products
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(Config.API_PORT))
