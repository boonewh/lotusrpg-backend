# lotusrpg/api/__init__.py
from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(api_bp)

# Enable CORS for frontend
CORS(api_bp, 
     origins=['http://localhost:3000'],  # React dev server
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Import and register all API routes
from lotusrpg.api.auth import routes as _auth_routes
from lotusrpg.api.rules import routes as _rules_routes
from lotusrpg.api.forum import routes as _forum_routes
from lotusrpg.api.admin import routes as _admin_routes
from lotusrpg.api.users import routes as _users_routes