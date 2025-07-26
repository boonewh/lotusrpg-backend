# lotusrpg/api/auth/routes.py
from flask import request, session
from flask_restful import Resource
from flask_security import login_user, logout_user, current_user
from flask_security.utils import verify_password, hash_password
from lotusrpg.models import User, db
from lotusrpg.schemas import user_schema, LoginSchema, RegisterSchema
from lotusrpg.api.base import BaseResource, api_response, api_error
from lotusrpg.api import api

class LoginResource(BaseResource):
    def post(self):
        """Login endpoint"""
        schema = LoginSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return api_error('Invalid email or password', 401)
        
        if user.is_banned:
            return api_error('Account is banned', 403)
        
        if user.is_locked():
            return api_error('Account is temporarily locked', 423)
        
        if not verify_password(data['password'], user.password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                from datetime import datetime, timedelta
                user.lockout_until = datetime.utcnow() + timedelta(minutes=30)
            db.session.commit()
            return api_error('Invalid email or password', 401)
        
        # Successful login
        user.failed_login_attempts = 0
        user.lockout_until = None
        db.session.commit()
        
        login_user(user)
        
        return api_response(
            data=user_schema.dump(user),
            message='Login successful'
        )

class LogoutResource(BaseResource):
    def post(self):
        """Logout endpoint"""
        logout_user()
        return api_response(message='Logout successful')

class RegisterResource(BaseResource):
    def post(self):
        """Registration endpoint"""
        schema = RegisterSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return api_error('Email already registered', 409)
        
        if User.query.filter_by(username=data['username']).first():
            return api_error('Username already taken', 409)
        
        # Create user
        import uuid
        user = User(
            email=data['email'],
            username=data['username'],
            password=hash_password(data['password']),
            fs_uniquifier=str(uuid.uuid4()),
            active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        return api_response(
            data=user_schema.dump(user),
            message='Registration successful',
            status=201
        )

class CurrentUserResource(BaseResource):
    def get(self):
        """Get current user info"""
        if current_user.is_authenticated:
            return api_response(data=user_schema.dump(current_user))
        return api_error('Not authenticated', 401)

# Register routes
api.add_resource(LoginResource, '/auth/login')
api.add_resource(LogoutResource, '/auth/logout')
api.add_resource(RegisterResource, '/auth/register')
api.add_resource(CurrentUserResource, '/auth/me')