# lotusrpg/api/users/routes.py
from flask import request
from flask_security import current_user
from lotusrpg.models import User, db
from lotusrpg.schemas import user_schema
from lotusrpg.api.base import AuthenticatedResource, api_response, api_error
from lotusrpg.api import api
from marshmallow import Schema, fields
import os
from werkzeug.utils import secure_filename
from PIL import Image
import secrets

class UserUpdateSchema(Schema):
    email = fields.Email()
    username = fields.Str(validate=lambda x: len(x.strip()) >= 2)

class UserProfileResource(AuthenticatedResource):
    def get(self):
        """Get current user's profile"""
        return api_response(data=user_schema.dump(current_user))
    
    def put(self):
        """Update current user's profile"""
        schema = UserUpdateSchema()
        try:
            data = schema.load(request.json)
        except Exception as e:
            return api_error('Invalid input data', 400)
        
        # Check email uniqueness
        if 'email' in data and data['email'] != current_user.email:
            if User.query.filter_by(email=data['email']).first():
                return api_error('Email already in use', 409)
            current_user.email = data['email']
        
        # Check username uniqueness
        if 'username' in data and data['username'] != current_user.username:
            if User.query.filter_by(username=data['username']).first():
                return api_error('Username already taken', 409)
            current_user.username = data['username']
        
        db.session.commit()
        
        return api_response(
            data=user_schema.dump(current_user),
            message='Profile updated successfully'
        )

class UserAvatarResource(AuthenticatedResource):
    def post(self):
        """Upload user avatar"""
        if 'avatar' not in request.files:
            return api_error('No avatar file provided', 400)
        
        file = request.files['avatar']
        if file.filename == '':
            return api_error('No file selected', 400)
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return api_error('Invalid file type. Use PNG, JPG, JPEG, or GIF', 400)
        
        # Generate unique filename
        random_hex = secrets.token_hex(8)
        f_ext = os.path.splitext(file.filename)[1]
        picture_fn = random_hex + f_ext
        
        # Save path (you'll need to ensure this directory exists)
        picture_path = os.path.join('lotusrpg/static/profile_pics', picture_fn)
        
        # Resize and save image
        try:
            output_size = (125, 125)
            img = Image.open(file)
            img.thumbnail(output_size)
            img.save(picture_path)
            
            # Delete old image if not default
            if current_user.image_file != 'default.png':
                old_path = os.path.join('lotusrpg/static/profile_pics', current_user.image_file)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Update user record
            current_user.image_file = picture_fn
            db.session.commit()
            
            return api_response(
                data={'image_file': picture_fn},
                message='Avatar updated successfully'
            )
            
        except Exception as e:
            return api_error('Error processing image', 500)

# Register routes
api.add_resource(UserProfileResource, '/users/profile')
api.add_resource(UserAvatarResource, '/users/avatar')