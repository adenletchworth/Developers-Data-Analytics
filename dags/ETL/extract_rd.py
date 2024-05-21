import praw
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from transformers import pipeline
from keybert import KeyBERT
from pymongo import MongoClient
from dotenv import load_dotenv

# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

load_dotenv()

class RedditExtractor:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        self.mongo_client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.mongo_client['reddit_db']
        self.collection = self.db['posts']
        self.ner_model = pipeline("ner", model="adenletchworth/CS-NER")
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.kw_model = KeyBERT()

    def preprocess_text(self, text):
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
        ner_results = self.ner_model(text)
        entities = [(result['word'], result['entity']) for result in ner_results]
        return entities

    def classify_and_extract_keywords(self, text, candidate_labels):
        if not text or not candidate_labels:
            raise ValueError("Text and candidate_labels must not be empty.")
        classification = self.classifier(text, candidate_labels)
        keywords = self.kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english')
        return classification, keywords

    def fetch_reddit_data(self, subreddit_name, limit=1):
        subreddit = self.reddit.subreddit(subreddit_name)
        hot_posts = subreddit.hot(limit=limit)
        posts_data = []
        for post in hot_posts:
            preprocessed_body = self.preprocess_text(post.selftext)
            print(f"Preprocessed body: {preprocessed_body}")  # Debugging print
            if preprocessed_body:  # Ensure the body is not empty
                entities = self.extract_entities(preprocessed_body)
                print(f"Entities: {entities}")  # Debugging print
                candidate_labels = ["technology", "business", "database", "programming", "career"]
                classification, keywords = self.classify_and_extract_keywords(preprocessed_body, candidate_labels)
                post_data = {
                    'title': post.title,
                    'created': post.created,
                    'body': preprocessed_body,
                    'entities': [entity for entity, tag in entities if tag != 'LABEL_27'],
                    'topic': classification['labels'][0],  # Get the top classified topic
                    'keywords': keywords,
                    'subreddit': str(post.subreddit)
                }
                posts_data.append(post_data)
                self.collection.insert_one(post_data)
        return posts_data

if __name__ == "__main__":
    reddit_extractor = RedditExtractor()
    subreddit_name = 'programming'
    posts = reddit_extractor.fetch_reddit_data(subreddit_name)

    for post in posts[:2]:  
        print(post)
  