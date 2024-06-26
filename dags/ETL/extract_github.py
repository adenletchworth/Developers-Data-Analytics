import requests
from dotenv import load_dotenv
import os
import base64

class GithubExtractor:
    def __init__(self):
        load_dotenv()  # Make sure to load the environment variables
        self.token = os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.events_url = "https://api.github.com/events"
        self.repo_url = "https://api.github.com/repos/{}"
        self.languages_url = "https://api.github.com/repos/{}/languages"
        self.readme_url = "https://api.github.com/repos/{}/readme"

    def get_event_repos(self):
        response = requests.get(self.events_url, headers=self.headers)
        if response.status_code == 200:
            events = response.json()
            repos = [event['repo']['name'] for event in events if event['type'] in ['PushEvent', 'ForkEvent', 'PullRequestEvent', 'WatchEvent']]
            return list(set(repos))
        else:
            print(f'Failed to fetch events: {response.status_code}')
            return None

    def get_repo_info(self, repo):
        response = requests.get(self.repo_url.format(repo), headers=self.headers)
        if response.status_code == 200:
            repo_data = response.json()
            languages = self.get_repo_languages(repo)
            readme = self.get_repo_readme(repo)
            return {
                'id': repo_data['id'],
                'name': repo_data['name'],
                'owner': {'login': repo_data['owner']['login'], 'id': repo_data['owner']['id']},
                'forks_count': repo_data['forks_count'],
                'stargazers_count': repo_data['stargazers_count'],
                'watchers_count': repo_data['watchers_count'],
                'description': repo_data['description'],
                'languages': languages,
                'readme': readme,
                'topics': repo_data['topics'],
                'license': repo_data['license']['name'] if repo_data['license'] else 'None',
                'created_at': repo_data['created_at'],
                'updated_at': repo_data['updated_at'],
                'has_issues': repo_data['has_issues'],
                'has_projects': repo_data['has_projects'],
                'has_wiki': repo_data['has_wiki'],
                'has_pages': repo_data['has_pages'],
                'has_downloads': repo_data['has_downloads'],
                'open_issues_count': repo_data['open_issues_count'],
                'forks': repo_data['forks'],
                'size': repo_data['size'],
            }
        else:
            print(f'Failed to fetch repo info: {response.status_code}')
            return None

    def get_repo_languages(self, repo):
        languages_response = requests.get(self.languages_url.format(repo), headers=self.headers)
        if languages_response.status_code == 200:
            return list(languages_response.json().keys())
        else:
            print(f'Failed to fetch repo languages: {languages_response.status_code}')
            return None

    def get_repo_readme(self, repo):
        response = requests.get(self.readme_url.format(repo), headers=self.headers)
        if response.status_code == 200:
            readme_data = response.json()
            readme_data['content'] = base64.b64decode(readme_data['content']).decode('utf-8')
            return readme_data['content'] 
        else:
            print(f'Failed to fetch repo README: {response.status_code}')
            return None
    
    def get(self):
        repos_info = []
        repos = self.get_event_repos()
        if not repos:
            return None
        
        for repo in repos:
            repo_info = self.get_repo_info(repo)
            if repo_info:
                repos_info.append(repo_info)
        
        return repos_info


if __name__ == '__main__':
    extractor = GithubExtractor()
    repos_info = extractor.get()
    print(repos_info)