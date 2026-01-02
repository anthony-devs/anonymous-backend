from flask_jwt_extended import JWTManager
from pymongo import MongoClient

jwt = JWTManager()

def get_mongo(app):
    """Return a MongoClient connected to the app's DB."""
    client = MongoClient(app.config["MONGO_URI"])
    return client[app.config["DB_NAME"]]
