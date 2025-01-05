from flask import Flask, jsonify, request
import requests
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_object(Config)

jwt = JWTManager(app)

# Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[Config.RATE_LIMIT]
)

# Microservices Mapping
SERVICES = Config.SERVICES

@app.route('/api/<service>/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@limiter.limit("10 per second")  # Limits each client to 10 requests per second
@jwt_required(optional=True)  # JWT Optional for now; Can enforce authentication later
def proxy(service, endpoint):
    """Routes API requests to the correct microservice"""
    if service not in SERVICES:
        return jsonify({"error": "Service not found"}), 404

    # Ensure API calls start with /api/ in the microservices
    url = f"{SERVICES[service]}/api/{endpoint}"  
    method = request.method
    headers = {key: value for key, value in request.headers if key != "Host"}
    data = request.get_json(silent=True)
    current_user = get_jwt_identity()

    try:
        if method == "GET":
            response = requests.get(url, params=request.args, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return jsonify({"error": "Method not allowed"}), 405

        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check for API Gateway"""
    return jsonify({"status": "API Gateway running"}), 200

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
