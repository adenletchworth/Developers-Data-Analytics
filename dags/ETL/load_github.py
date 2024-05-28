from pymongo import MongoClient
import json

def load_data_into_mongodb(data):
    if not data:
        print("No data to load into MongoDB")
        return
    
    connection_string = "mongodb://host.docker.internal:27017/"
    client = MongoClient(connection_string)
    
    db = client["Developer"]
    collection = db["github_repos_raw"]

    if isinstance(data, str):
        data = json.loads(data)

    if isinstance(data, list):
        for record in data:
            if isinstance(record, str):
                record = json.loads(record)

            clean_record = {k: v for k, v in record.items() if v not in [None, '', []]}
            repo_id = clean_record.get('repo_id')

            try:
                if repo_id is not None:
                    collection.update_one({'repo_id': repo_id}, {'$set': clean_record}, upsert=True)
                else:
                    collection.insert_one(clean_record)
            except Exception as e:
                print(f"Error inserting record: {e}")
    else:
        print("Data is not in the expected format (list of dictionaries).")

    print("Data loaded successfully.")
    client.close()
