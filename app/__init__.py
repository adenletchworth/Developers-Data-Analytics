import logging
from flask import Flask, g
from flask_cors import CORS
from flask_caching import Cache
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from app.extensions import cache

load_dotenv()  

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    app.config['MONGO_URI'] = "mongodb://localhost:27017/Developer"  

    # Initialize MongoDB client
    client = MongoClient(app.config['MONGO_URI'])
    app.db = client.get_database('Developer')  

    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    cache.init_app(app)

    # Register Blueprints
    from app.routes import main
    app.register_blueprint(main)

    @app.teardown_appcontext
    def teardown_models(exception):
        models = g.pop('models', None)
        if models is not None:
            logger.info("Stopping Spark session")
            models.spark.stop()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
