# /opt/airflow/dags/ETL/extract_reddit.py

import praw
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from keybert import KeyBERT
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from .ner_module import NamedEntityRecognizer 
import logging

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

load_dotenv()

class RedditExtractor:
    def __init__(self, named_entity_recognizer=None, keybert=None):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        self.mongo_client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.mongo_client['reddit_db']
        self.collection = self.db['posts']
        self.ner_model = NamedEntityRecognizer("adenletchworth/CS-NER")
        self.kw_model = KeyBERT()

        # Check MongoDB connection
        try:
            self.mongo_client.server_info()  
            logging.info("MongoDB server is accessible")
        except errors.ServerSelectionTimeoutError as err:
            logging.error(f"Error: {err}")
            raise

    def preprocess_text(self, text):
        if text is None:
            return ""
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        return ' '.join(tokens)

    def extract_entities(self, text):
        try:
            entities = self.ner_model.predict(text)
            return entities
        except Exception as e:
            logging.error(f"Error extracting entities: {e}")
            return []

    def extract_keywords(self, text):
        try:
            keywords = self.kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english')
            return [kw[0] for kw in keywords]
        except Exception as e:
            logging.error(f"Error extracting keywords: {e}")
            return []

    def fetch_reddit_data(self, subreddit_name, limit=1):
        subreddit = self.reddit.subreddit(subreddit_name)
        hot_posts = subreddit.hot(limit=limit)
        posts_data = []
        for post in hot_posts:
            preprocessed_body = self.preprocess_text(post.selftext)
            logging.info(f"Preprocessed body: {preprocessed_body}")  # Debugging print
            if preprocessed_body:  # Ensure the body is not empty
                entities = self.extract_entities(preprocessed_body)
                logging.info(f"Entities: {entities}")  # Debugging print
                keywords = self.extract_keywords(preprocessed_body)
                post_data = {
                    'title': post.title,
                    'created': post.created,
                    'body': preprocessed_body,
                    'entities': entities,
                    'keywords': keywords,
                    'subreddit': str(post.subreddit)
                }
                posts_data.append(post_data)
                try:
                    self.collection.insert_one(post_data)
                    logging.info(f"Post data inserted: {post_data}")
                except errors.PyMongoError as e:
                    logging.error(f"Error inserting post data into MongoDB: {e}")

        return posts_data

if __name__ == "__main__":
    reddit_extractor = RedditExtractor()
    subreddit_name = 'programming'
    posts = reddit_extractor.fetch_reddit_data(subreddit_name)

    for post in posts[:2]:  
        print(post)
