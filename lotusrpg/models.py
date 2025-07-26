from flask import current_app as app
from lotusrpg import db
from datetime import datetime, timedelta
from flask_security import UserMixin, RoleMixin

# Association table for many-to-many relationship between users and roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"Role('{self.name}', '{self.description}')"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    is_banned = db.Column(db.Boolean(), default=False)

    # Tracking columns
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer, default=0)
    failed_login_attempts = db.Column(db.Integer, default=0)
    lockout_until = db.Column(db.DateTime, nullable=True)

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.active}')"

    def is_locked(self):
        """Check if the user account is temporarily locked"""
        if self.lockout_until and self.lockout_until > datetime.utcnow():
            return True
        # Reset lockout if time has expired
        if self.lockout_until and self.lockout_until <= datetime.utcnow():
            self.reset_lockout()
        return False

    def reset_lockout(self):
        """Reset failed login attempts after lockout period expires"""
        self.failed_login_attempts = 0
        self.lockout_until = None
        db.session.commit()

    def is_active(self):
        """Override UserMixin is_active to check for locks and bans"""
        return self.active and not self.is_banned and not self.is_locked()

    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)  # Add this relationship

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    user = db.relationship('User', backref='comments', lazy=True)

    def __repr__(self):
        return f"Comment('{self.content}', User ID: {self.user_id}, Post ID: {self.post_id})"


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)
    chapter = db.Column(db.String(255), nullable=False) 
    rulebook = db.Column(db.String(50), nullable=False, default='core')  # 'core' or 'darkholme'

    children = db.relationship('Section', backref='parent', remote_side=[id])
    images = db.relationship('Image', back_populates='section', cascade='all, delete-orphan')


    def __repr__(self):
        return f"Section('{self.title}', Slug: '{self.slug}', Parent ID: {self.parent_id})"


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    content_type = db.Column(db.Enum("heading", "subheading", "paragraph", "table", "list", "image", "container", "link", name="content_types"), nullable=False)
    content_order = db.Column(db.Integer, nullable=False)
    content_data = db.Column(db.JSON, nullable=False)
    style_class = db.Column(db.String(255), nullable=True)

    section = db.relationship('Section', backref='contents')

    def __repr__(self):
        return f"Content('{self.content_type}', Order: {self.content_order}, Section ID: {self.section_id})"


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255), nullable=True)
    class_name = db.Column(db.String(255), nullable=True) 
    section_id = db.Column(db.Integer, db.ForeignKey('section.id')) 

    section = db.relationship('Section', back_populates='images') 

    def __repr__(self):
        return f"Image('{self.file_path}', Alt Text: '{self.alt_text}', Class: '{self.class_name}')"
