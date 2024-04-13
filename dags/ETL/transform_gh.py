def get_popularity(forks_count, stargazers_count, watchers_count):
    popularity_score = forks_count + stargazers_count + watchers_count
    return 0 if popularity_score < 10 else 1 if popularity_score < 100 else 2
    
def get_topics(description, nlp):
    if description:  
        doc = nlp(description)
        filtered_tokens = [token.text for token in doc if not token.is_stop]
        filtered_text = " ".join(filtered_tokens)
        doc = nlp(filtered_text) 
        named_entities = [entity.text for entity in doc.ents]
        return named_entities
    return []

def transform(data, nlp):
    transformed_data = []
    for repo_info in data:
        transformed_data.append({
            'id': repo_info['id'],
            'name': repo_info['name'],
            'owner': repo_info['owner'],
            'forks_count': repo_info['forks_count'],
            'stargazers_count': repo_info['stargazers_count'],
            'watchers_count': repo_info['watchers_count'],
            'description': repo_info['description'],
            'languages': ', '.join(repo_info.get('languages', [])),  
            'popularity': get_popularity(repo_info['forks_count'], repo_info['stargazers_count'], repo_info['watchers_count']),
            'topics': repo_info['topics'], 
            'custom_topics': get_topics(repo_info.get('description'), nlp) ,
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
            'size': repo_info['size']
        })

    return transformed_data

