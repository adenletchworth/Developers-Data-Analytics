import spacy

nlp = spacy.load('../NER/models/spacy_word2vec_model')

def get_popularity(forks_count, stargazers_count, watchers_count):
    popularity_score = forks_count + stargazers_count + watchers_count
    return 0 if popularity_score < 10 else 1 if popularity_score < 100 else 2
    
def get_topics(description):
    if description:  
        doc = nlp(description)
        filtered_tokens = [token.text for token in doc if not token.is_stop]
        filtered_text = " ".join(filtered_tokens)
        doc = nlp(filtered_text) 
        named_entities = [entity.text for entity in doc.ents]
        return named_entities
    return []

def transform(data):
    transformed_data = []
    for repo_info in data:
        transformed_data.append({
            'forks_count': repo_info['forks_count'],
            'stargazers_count': repo_info['stargazers_count'],
            'watchers_count': repo_info['watchers_count'],
            'description': repo_info['description'],
            'languages': ', '.join(repo_info.get('languages', [])),  
            'popularity': get_popularity(repo_info['forks_count'], repo_info['stargazers_count'], repo_info['watchers_count']),
            'topics': get_topics(repo_info.get('description')) 
        })
    return transformed_data

