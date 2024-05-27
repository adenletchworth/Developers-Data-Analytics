import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from .ner_module import NamedEntityRecognizer  
from keybert import KeyBERT
import gzip
import base64

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class DataTransformer:
    def __init__(self):
        self.url_pattern = re.compile(r'http\S+|www\S+|https\S+')
        self.html_pattern = re.compile(r'<.*?>')
        self.non_word_pattern = re.compile(r'[^\w\s]')
        self.entity_model = NamedEntityRecognizer('adenletchworth/CS-NER')
        self.kw_model = KeyBERT()
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def compress_text(self, text):
        compressed_data = gzip.compress(text.encode('utf-8'))
        return base64.b64encode(compressed_data).decode('utf-8')

    def preprocess_text(self, text):
        if text is None:
            return ""
        text = text.lower()
        text = self.url_pattern.sub('', text)
        text = self.html_pattern.sub('', text)
        text = self.non_word_pattern.sub('', text)
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in self.stop_words]
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        return ' '.join(tokens)

    def get_topics(self, description):
        if description is None:
            return []
        topics = self.entity_model.predict(description)
        return list(set(topics))

    def extract_keywords(self, text):
        if not text:
            return []
        keywords = self.kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english')
        return list(set(kw[0] for kw in keywords))

    def transform(self, data):
        if data is None:
            print("No data to transform")
            return None

        transformed_data = []
        for repo_info in data:
            description = repo_info.get('description')
            preprocessed_description = self.preprocess_text(description)
            custom_topics = self.get_topics(description)
            keywords = self.extract_keywords(preprocessed_description)

            readme_preprocessed = self.preprocess_text(repo_info['readme'])
            readme_topics = self.get_topics(readme_preprocessed)
            readme_keywords = self.extract_keywords(readme_preprocessed)

            print(readme_keywords)
            
            transformed_data.append({
                'id': repo_info['id'],
                'name': repo_info['name'],
                'owner': repo_info['owner'],
                'forks_count': repo_info['forks_count'],
                'stargazers_count': repo_info['stargazers_count'],
                'watchers_count': repo_info['watchers_count'],
                'description': description,
                'languages': ', '.join(repo_info.get('languages', [])),  
                'topics': repo_info['topics'], 
                'custom_topics': custom_topics,
                'keywords': keywords,
                'license': repo_info['license'],
                'created_at': repo_info['created_at'],
                'updated_at': repo_info['updated_at'],
                'has_issues': repo_info['has_issues'],
                'has_projects': repo_info['has_projects'],
                'has_wiki': repo_info['has_wiki'],
                'has_pages': repo_info['has_pages'],
                'has_downloads': repo_info['has_downloads'],
                'open_issues_count': repo_info['open_issues_count'],
                'forks': repo_info['forks'],
                'size': repo_info['size'],
                'readme_topics': readme_topics,
                'readme_keywords': readme_keywords,
                'readme_preprocessed': self.compress_text(readme_preprocessed)
            })

        return transformed_data
