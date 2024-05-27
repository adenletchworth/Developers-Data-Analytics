from confluent_kafka import Producer
import json
from ETL.extract_github import GithubExtractor

def github_producer():
    p = Producer({'bootstrap.servers': 'kafka:9092'})
    extractor = GithubExtractor()
    repos_info = extractor.get()

    for repo in repos_info:
        p.produce('github_topic', key=str(repo['id']), value=json.dumps(repo))

    p.flush()

if __name__ == "__main__":
    github_producer()
