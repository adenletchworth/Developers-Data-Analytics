from confluent_kafka import Producer
import json
from ETL.extract_reddit import RedditExtractor

def reddit_producer():
    p = Producer({'bootstrap.servers': 'kafka:9092'})

    # Extract data using your custom extractor
    extractor = RedditExtractor()
    subreddit_name = 'programming'
    posts = extractor.fetch_reddit_data(subreddit_name)

    for post in posts:
        if '_id' in post:
            post['_id'] = str(post['_id'])
        p.produce('reddit_topic', key=post['_id'], value=json.dumps(post))

    p.flush()

if __name__ == "__main__":
    reddit_producer()
