from pymongo import MongoClient

def load_data_into_mongodb(data):
    connection_string = "mongodb://host.docker.internal:27017/"
    client = MongoClient(connection_string)
    
    db = client["github_db"]
    collection = db["developer_stats"]
    
    for record in data:
        clean_record = {k: v for k, v in record.items() if v not in [None, '', []]}
        repo_id = clean_record.get('repo_id')

        if repo_id is not None:
            collection.update_one({'repo_id': repo_id}, {'$set': clean_record}, upsert=True)
        else:
            collection.insert_one(clean_record)

    print("Data loaded successfully.")
    client.close()

    



