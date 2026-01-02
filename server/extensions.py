from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from flask import current_app

jwt = JWTManager()
mongo_client = None

def init_mongo(app):
    global mongo_client
    mongo_client = MongoClient(app.config["MONGO_URI"])
    return mongo_client[app.config["DB_NAME"]]
