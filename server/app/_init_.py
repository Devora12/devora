from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Load config
    from .config import Config
    app.config.from_object(Config)
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"]
        }
    }, supports_credentials=True)
    
    # Initialize database
    from .database import init_db
    init_db(app)
    
    # Register routes
    from .routes import register_routes
    register_routes(app)
    
    return app