# lotusrpg/api/base.py
from flask_restful import Resource
from flask_security import auth_required, roles_required
from functools import wraps
import json

class BaseResource(Resource):
    """Base class for all API resources with common functionality"""
    
    def dispatch_request(self, *args, **kwargs):
        # Add common headers
        response = super().dispatch_request(*args, **kwargs)
        if hasattr(response, 'headers'):
            response.headers['Content-Type'] = 'application/json'
        return response

class AuthenticatedResource(BaseResource):
    """Base class for authenticated endpoints"""
    decorators = [auth_required()]

class AdminResource(BaseResource):
    """Base class for admin-only endpoints"""
    decorators = [roles_required('admin')]

def api_response(data=None, message=None, status=200, **kwargs):
    """Standardized API response format"""
    response = {
        'success': status < 400,
        'status': status,
        'message': message,
        'data': data,
        **kwargs
    }
    return response, status

def api_error(message, status=400, **kwargs):
    """Standardized error response"""
    return api_response(message=message, status=status, **kwargs)