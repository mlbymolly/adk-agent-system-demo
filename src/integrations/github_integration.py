# GitHub API Integration Utilities

"""
This module contains utilities for managing and fetching issues and pull requests using the GitHub API.
"""

import requests
from typing import List, Dict, Any, Optional

class GitHubAPI:
    def __init__(self, token: str, repo_owner: str, repo_name: str):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def fetch_issues(self, state: str = 'open') -> List[Dict[str, Any]]:
        """
        Fetch a list of issues from the repository.
        """
        url = f'{self.base_url}/issues'
        params = {'state': state}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def fetch_pull_requests(self, state: str = 'open') -> List[Dict[str, Any]]:
        """
        Fetch a list of pull requests from the repository.
        """
        url = f'{self.base_url}/pulls'
        params = {'state': state}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def create_issue(self, title: str, body: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new issue in the repository.
        """
        url = f'{self.base_url}/issues'
        issue = {'title': title, 'body': body}
        if labels:
            issue['labels'] = labels
        response = requests.post(url, json=issue, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def merge_pull_request(self, pull_number: int, commit_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Merge a pull request by its number.
        """
        url = f'{self.base_url}/pulls/{pull_number}/merge'
        data = {}
        if commit_title:
            data['commit_title'] = commit_title
        response = requests.put(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_pull_request_files(self, pull_number: int) -> List[Dict[str, Any]]:
        """
        Get files changed in a pull request.
        """
        url = f'{self.base_url}/pulls/{pull_number}/files'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
