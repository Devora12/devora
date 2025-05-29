from pymongo import MongoClient
from flask import current_app

db_client = None
db = None

def init_db(app):
    global db_client, db
    try:
        db_client = MongoClient(app.config['MONGO_URI'])
        db = db_client[app.config['DATABASE_NAME']]
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

def get_collection(collection_name=None):
    collection_name = collection_name or current_app.config['COLLECTION_NAME']
    return db[collection_name]