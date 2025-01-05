from flask import request, jsonify
import jsonschema
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ✅ Pagination Middleware (Fixes response issue)
def paginate_data(f):
    """Middleware for paginating GET requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)

        # Ensure response is properly unpacked (Flask response or tuple)
        if isinstance(response, tuple):
            data, status_code = response
            data = data.get_json()
        else:
            data = response.get_json()
            status_code = 200

        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        start = (page - 1) * limit
        end = start + limit
        paginated_data = data[start:end]

        return jsonify({
            "page": page,
            "limit": limit,
            "total": len(data),
            "results": paginated_data
        }), status_code

    return decorated_function

# ✅ Filtering & Sorting Middleware (Fixes response issue)
def filter_and_sort_data(f):
    """Middleware for filtering and sorting GET requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)

        # Ensure response is properly unpacked (Flask response or tuple)
        if isinstance(response, tuple):
            data, status_code = response
            data = data.get_json()
        else:
            data = response.get_json()
            status_code = 200

        sort_by = request.args.get("sort_by")
        order = request.args.get("order", "asc")
        filter_key = request.args.get("filter_key")
        filter_value = request.args.get("filter_value")

        # Apply filtering
        if filter_key and filter_value:
            data = [item for item in data if str(item.get(filter_key, "")).lower() == filter_value.lower()]

        # Apply sorting
        if sort_by:
            reverse = order.lower() == "desc"
            data = sorted(data, key=lambda x: x.get(sort_by, ""), reverse=reverse)

        return jsonify(data), status_code

    return decorated_function
def handle_errors(f):
    """Middleware to catch missing resources & validation errors."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            return jsonify({"error": f"Missing key: {str(e)}"}), 400
        except jsonschema.exceptions.ValidationError as e:
            return jsonify({"error": "Invalid request data", "message": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    return decorated_function

# ✅ Validation Middleware
def validate_json(schema):
    """Middleware to validate JSON requests based on a schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                jsonschema.validate(instance=request.json, schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                return jsonify({"error": "Invalid request data", "message": str(e)}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ✅ Prevent Duplicate Cart Entries
def prevent_duplicates(f):
    """Middleware to prevent duplicate cart entries"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from utils.database import cart_db
        data = request.json
        user_id = data.get("user_id")
        product_id = data.get("product_id")

        existing_item = next(
            (item for item in cart_db if item["user_id"] == user_id and item["product_id"] == product_id),
            None
        )

        if existing_item:
            return jsonify({"error": "Product already in cart"}), 400

        return f(*args, **kwargs)
    return decorated_function

# ✅ Role-Based Access Control (RBAC) - Only Admins Can Modify Orders
def admin_required(f):
    """Middleware to allow only admins to access certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from utils.database import users_db
        user_id = request.headers.get("X-User-Id")
        user = next((u for u in users_db if u["id"] == user_id), None)

        if not user or user.get("role") != "admin":
            return jsonify({"error": "Unauthorized. Admin role required."}), 403
        
        return f(*args, **kwargs)
    return decorated_function

