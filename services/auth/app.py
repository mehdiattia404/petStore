from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_swagger_ui import get_swaggerui_blueprint
import json
import sys
import os
from config import Config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.database import users_db

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "*"}})



# Swagger UI setup
SWAGGER_URL = "/swagger"
API_URL = "/static/openapi.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Auth Service API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/openapi.yaml')
def get_openapi_yaml():
    """Serve OpenAPI YAML file"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "openapi.yaml", mimetype="text/yaml")

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registers a new user"""
    data = request.json
    for user in users_db:
        if user["username"] == data["username"]:
            return jsonify({"message": "User already exists"}), 400
    
    new_user = {
        "id": f"user-{len(users_db) + 1}",
        "username": data["username"],
        "email": data["email"],
        "password": data["password"],  # Hashing should be added in production
        "role": "customer"
    }
    
    users_db.append(new_user)
    
    # Save back to the mock database
    with open("mock_database.json", "w") as file:
        json.dump({"users": users_db}, file, indent=4)
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login and JWT token generation"""
    data = request.json
    for user in users_db:
        if user["username"] == data["username"] and user["password"] == data["password"]:
            token = create_access_token(identity={"id": user["id"], "username": user["username"], "role": user["role"]})
            return jsonify(access_token=token), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_user():
    """Retrieve user details from JWT token"""
    current_user = get_jwt_identity()
    return jsonify(current_user), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(Config.API_PORT))
