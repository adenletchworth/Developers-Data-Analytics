import requests

class GithubExtractor:
    def __init__(self):
        self.events_url = "https://api.github.com/events"
        self.repo_url = "https://api.github.com/repos/{}"  
        self.languages_url = "https://api.github.com/repos/{}/languages"  

    def get_event_repos(self):
        response = requests.get(self.events_url)
        if response.status_code == 200:
            events = response.json()
            repos = [event['repo']['name'] for event in events if event['type'] in ['PushEvent', 'ForkEvent', 'PullRequestEvent', 'WatchEvent']]
            return list(set(repos))
        else:
            print(f'Failed to fetch events: {response.status_code}')
            return None

    def get_repo_info(self, repo):
        response = requests.get(self.repo_url.format(repo))
        if response.status_code == 200:
            repo_data = response.json()
            languages = self.get_repo_languages(repo)
            
            return {
            'forks_count': repo_data['forks_count'],
            'stargazers_count': repo_data['stargazers_count'],
            'watchers_count': repo_data['watchers_count'],
            'description': repo_data['description'],
            'languages': languages
        }
        else:
            print(f'Failed to fetch repo info: {response.status_code}')
            return None

    def get_repo_languages(self, repo):
        languages_response = requests.get(self.languages_url.format(repo))
        if languages_response.status_code == 200:
            return list(languages_response.json().keys())
        else:
            print(f'Failed to fetch repo languages: {languages_response.status_code}')
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
            
extractor = GithubExtractor()
repos_info = extractor.get()
print(repos_info)

        
        
