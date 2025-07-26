# lotusrpg/schemas/__init__.py
from marshmallow import Schema, fields, post_load, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from lotusrpg.models import User, Section, Content, Post, Comment

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password', 'fs_uniquifier')
        
    roles = fields.Method('get_role_names')
    is_locked = fields.Method('get_is_locked')
    
    def get_role_names(self, obj):
        return [role.name for role in obj.roles]
    
    def get_is_locked(self, obj):
        return obj.is_locked()

class ContentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Content
        load_instance = True
        
    # Handle JSON content_data properly
    content_data = fields.Raw()

class SectionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Section
        load_instance = True
        
    contents = fields.Nested(ContentSchema, many=True, dump_only=True)
    content_count = fields.Method('get_content_count')
    
    def get_content_count(self, obj):
        return len(obj.contents)

class PostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        load_instance = True
        
    author = fields.Nested(UserSchema, dump_only=True)
    comment_count = fields.Method('get_comment_count')
    excerpt = fields.Method('get_excerpt')
    
    def get_comment_count(self, obj):
        return len(obj.comments)
    
    def get_excerpt(self, obj, length=200):
        if len(obj.content) <= length:
            return obj.content
        return obj.content[:length] + '...'

class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        load_instance = True
        
    user = fields.Nested(UserSchema, dump_only=True)

# Request/Response Schemas
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 6)

class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=lambda x: len(x) >= 2)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 6)

class SectionCreateSchema(Schema):
    title = fields.Str(required=True)
    slug = fields.Str(required=True)
    chapter = fields.Str(required=True)
    rulebook = fields.Str(required=True, validate=lambda x: x in ['core', 'darkholme'])
    parent_id = fields.Int(allow_none=True)

class ContentCreateSchema(Schema):
    section_id = fields.Int(required=True)
    content_type = fields.Str(required=True)
    content_order = fields.Int(required=True)
    content_data = fields.Raw(required=True)
    style_class = fields.Str(allow_none=True)

# Pagination Schema - FIXED
class PaginationSchema(Schema):
    page = fields.Int(load_default=1, validate=lambda x: x > 0)
    per_page = fields.Int(load_default=10, validate=lambda x: 1 <= x <= 100)
    search = fields.Str(load_default=None, allow_none=True)

# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
section_schema = SectionSchema()
sections_schema = SectionSchema(many=True)
content_schema = ContentSchema()
contents_schema = ContentSchema(many=True)
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)