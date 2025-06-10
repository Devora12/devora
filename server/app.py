from flask import Flask
from flask_cors import CORS
from database import init_db
from routes import register_routes
from config import Config

def create_app():
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(Config)
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173" , "*"]
        }
    }, supports_credentials=True)
    
    # Initialize database
    init_db(app)
    
    # Register routes
    register_routes(app)
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=2001, host='0.0.0.0')
