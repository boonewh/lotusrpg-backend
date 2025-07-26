# lotusrpg/__init__.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
security = Security()

def create_app(config_class='lotusrpg.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models here to avoid circular imports
    from lotusrpg.models import User, Role
    
    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
    
    # Import and register API blueprint
    from lotusrpg.api import api_bp
    app.register_blueprint(api_bp)
    
    # Import and initialize WebSocket
    from lotusrpg.websockets import socketio
    socketio.init_app(app, async_mode='threading')
    
    # Note: All API routes are automatically registered through the api_bp blueprint
    # The routes in lotusrpg/api/* are imported by lotusrpg/api/__init__.py
    
    # Add a catch-all route for React app (for production)
    @app.route('/')
    def serve_react_app():
        # In development, this serves your existing index.html
        # In production, this would serve the built React app
        return render_template('index.html')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'version': '1.0.0'}
    
    return app