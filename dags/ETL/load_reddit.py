import os
from pymongo import MongoClient, errors
import logging

def load_data_into_mongodb(data):
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client['reddit_db']
        collection = db['repos']
        
        if data:
            for record in data:
                # Check for duplicates and upsert
                filter_query = {'_id': record['_id']}
                update_query = {'$set': record}
                collection.update_one(filter_query, update_query, upsert=True)
            logging.info(f"Inserted/Updated {len(data)} records into MongoDB collection 'repos'.")
        else:
            logging.warning("No data to insert into MongoDB.")
        
    except errors.PyMongoError as e:
        logging.error(f"An error occurred while inserting data into MongoDB: {e}")
    finally:
        client.close()
