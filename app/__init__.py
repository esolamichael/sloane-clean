# app/__init__.py
import os
from flask import Flask
from .database import mongo

def create_app(test_config=None):
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_for_development_only'),
        MONGODB_URL=os.environ.get('MONGODB_URL', 'mongodb://localhost:27017'),
        MONGODB_NAME=os.environ.get('MONGODB_NAME', 'sloane_ai_service'),
    )
    
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Initialize database
    mongo.init_app(app)
    
    # Register blueprints
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from .business.routes import business_bp
    app.register_blueprint(business_bp)
    
    # Add a simple route for testing
    @app.route('/ping')
    def ping():
        return {'status': 'healthy', 'service': 'Sloane AI Phone Service'}
    
    return app
