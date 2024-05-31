from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  

def create_app():
    app = Flask(__name__)

    app.config['MONGO_URI'] = "mongodb://localhost:27017/Developer"  

    # Initialize MongoDB client
    client = MongoClient(app.config['MONGO_URI'])
    app.db = client.get_database('Developer')  

    # Register Blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
