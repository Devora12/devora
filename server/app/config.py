import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/qa_management')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'QA')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'devora_function')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')