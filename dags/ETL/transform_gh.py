def get_popularity(forks_count, stargazers_count, watchers_count):
    popularity_score = forks_count + stargazers_count + watchers_count
    return 0 if popularity_score < 10 else 1 if popularity_score < 100 else 2
    
def get_topics(description, entity_model):
    if description is None:
        return []
    
    topics = entity_model.predict(description)
    return topics

def transform(data, entity_model):
    if data is None:
        print("No data to transform")
        return None
    
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
            'custom_topics': get_topics(repo_info.get('description'), entity_model) ,
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

data = [
    {'id': 787243240, 'name': 'Project-Checkers', 'owner': {'login': 'nowherecat65', 'id': 55722162}, 'forks_count': 0, 'stargazers_count': 0, 'watchers_count': 0, 'description': None, 'languages': [], 'topics': [], 'license': 'None', 'created_at': '2024-04-16T06:49:30Z', 'updated_at': '2024-05-05T02:36:28Z', 'has_issues': True, 'has_projects': True, 'has_wiki': True, 'has_pages': False, 'has_downloads': True, 'open_issues_count': 0, 'forks': 0, 'size': 52501},
    {'id': 795454409, 'name': 'ROS2-Turtlesim-Catch_Them_All-Project', 'owner': {'login': 'LateefAkinola', 'id': 105966848}, 'forks_count': 0, 'stargazers_count': 0, 'watchers_count': 0, 'description': '...', 'languages': ['Python', 'CMake'], 'topics': [], 'license': 'None', 'created_at': '2024-05-03T10:12:55Z', 'updated_at': '2024-05-05T02:40:34Z', 'has_issues': True, 'has_projects': True, 'has_wiki': True, 'has_pages': False, 'has_downloads': True, 'open_issues_count': 0, 'forks': 0, 'size': 25},
    {'id': 777500890, 'name': 'blockchain', 'owner': {'login': 'VCFAdvisor', 'id': 41657478}, 'forks_count': 0, 'stargazers_count': 0, 'watchers_count': 0, 'description': None, 'languages': ['Shell'], 'topics': [], 'license': 'None', 'created_at': '2024-03-26T00:53:51Z', 'updated_at': '2024-05-05T02:36:53Z', 'has_issues': True, 'has_projects': True, 'has_wiki': True, 'has_pages': False, 'has_downloads': True, 'open_issues_count': 0, 'forks': 0, 'size': 62660},
    {'id': 789952325, 'name': 'MDAgents', 'owner': {'login': 'mitmedialab', 'id': 7405700}, 'forks_count': 1, 'stargazers_count': 5, 'watchers_count': 5, 'description': None, 'languages': ['Python'], 'topics': [], 'license': 'None', 'created_at': '2024-04-22T01:29:05Z', 'updated_at': '2024-05-05T02:36:27Z', 'has_issues': True, 'has_projects': True, 'has_wiki': True, 'has_pages': False, 'has_downloads': True, 'open_issues_count': 0, 'forks': 1, 'size': 24},
    {'id': 50007393, 'name': 'jackson-datatypes-collections', 'owner': {'login': 'FasterXML', 'id': 382692}, 'forks_count': 51, 'stargazers_count': 73, 'watchers_count': 73, 'description': 'Jackson project that contains various collection-oriented datatype libraries: Eclipse Collections, Guava, HPPC, PCollections', 'languages': ['Java', 'Logos', 'Python'], 'topics': ['eclipse-collections', 'guava', 'hacktoberfest', 'jackson'], 'license': 'Apache License 2.0', 'created_at': '2016-01-20T05:39:06Z', 'updated_at': '2024-05-05T02:39:11Z', 'has_issues': True, 'has_projects': True, 'has_wiki': True, 'has_pages': True, 'has_downloads': True, 'open_issues_count': 8, 'forks': 51, 'size': 3178},
    {'id': 569191309, 'name': 'yarb', 'owner': {'login': 'NATIVE99', 'id': 35191800}, 'forks_count': 0, 'stargazers_count': 0, 'watchers_count': 0, 'description': 'Yet Another React Boilerplate', 'languages': ['JavaScript', 'HTML', 'CSS'], 'topics': ['react', 'boilerplate', 'react-boilerplate'], 'license': 'MIT License', 'created_at': '2016-04-25T14:52:00Z', 'updated_at': '2024-05-05T02:39:11Z', 'has_issues': True, 'has_projects': True, 'has_wiki': True, 'has_pages': True, 'has_downloads': True, 'open_issues_count': 0, 'forks': 0, 'size': 0},
]

# from ner_module import NamedEntityRecognizer
# transformed_data = transform(data, NamedEntityRecognizer('adenletchworth/CS-NER'))

# print(transformed_data)
