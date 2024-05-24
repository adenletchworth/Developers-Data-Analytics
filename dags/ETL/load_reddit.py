import os
from pymongo import MongoClient, errors
import logging

def load_data_into_mongodb(data):
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client['reddit_db']
        collection = db['repos']
        
        if data:
            collection.insert_many(data)
            logging.info(f"Inserted {len(data)} records into MongoDB collection 'repos'.")
        else:
            logging.warning("No data to insert into MongoDB.")
        
    except errors.PyMongoError as e:
        logging.error(f"An error occurred while inserting data into MongoDB: {e}")
    finally:
        client.close()
