# GitHub API Integration Utilities

"""
This module contains utilities for managing and fetching issues and pull requests using the GitHub API.
"""

import requests

class GitHubAPI:
    def __init__(self, token, repo_owner, repo_name):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'
        self.headers = {'Authorization': f'token {self.token}'}

    def fetch_issues(self):
        """
        Fetch a list of issues from the repository.
        """
        url = f'{self.base_url}/issues'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def fetch_pull_requests(self):
        """
        Fetch a list of pull requests from the repository.
        """
        url = f'{self.base_url}/pulls'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def create_issue(self, title, body):
        """
        Create a new issue in the repository.
        """
        url = f'{self.base_url}/issues'
        issue = {'title': title, 'body': body}
        response = requests.post(url, json=issue, headers=self.headers)
        return response.json()

    def merge_pull_request(self, pull_number):
        """
        Merge a pull request by its number.
        """
        url = f'{self.base_url}/pulls/{pull_number}/merge'
        response = requests.put(url, headers=self.headers)
        return response.json()  

# Usage Example
# github = GitHubAPI('your_access_token', 'repo_owner', 'repo_name')
# issues = github.fetch_issues()
# pulls = github.fetch_pull_requests()