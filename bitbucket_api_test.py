#!/usr/bin/env python3
"""
Bitbucket Server/Data Center REST API Test Script

This script tests all the Bitbucket Server REST API endpoints defined in the MCP Server project.
Fill in the configuration variables below and run the script to test API connectivity and functionality.

Author: Abbhishek Aditya BS
"""

import requests
import json
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Optional, Any
import sys

# =============================================================================
# CONFIGURATION - UPDATE THESE VARIABLES
# =============================================================================

# Bitbucket Server configuration
BASE_URL = "https://your-bitbucket-server.company.com"  # Your Bitbucket Server URL
PROJECT_KEY = "YOUR_PROJECT"                             # Project key (e.g., "PROJ")
REPOSITORY_NAME = "your-repository-name"                 # Repository name
PERSONAL_ACCESS_TOKEN = "your-personal-access-token"     # Your personal access token

# Test data placeholders
TEST_BRANCH_NAME = "feature/test-branch"
TEST_BASE_BRANCH = "main"
TEST_TAG_NAME = "v1.0.0"
TEST_PR_ID = "1"
TEST_COMMIT_MESSAGE = "Test commit message"
TEST_SEARCH_QUERY = "function"
TEST_FILE_PATH = "src/main/java/Main.java"

# =============================================================================
# API CLIENT CLASS
# =============================================================================

class BitbucketServerAPI:
    """Bitbucket Server REST API client for testing MCP functionality"""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            print(f"\n{method} {endpoint}")
            print(f"Status: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    print(f"Response: {json.dumps(response.json(), indent=2)}")
                except:
                    print(f"Response: {response.text}")
            else:
                print(f"Response: {response.text[:200]}...")
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    # =============================================================================
    # REPOSITORY OPERATIONS
    # =============================================================================
    
    def list_repositories(self, project_key: str, limit: int = 100) -> Optional[Dict]:
        """List all repositories in a project"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos"
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.json() if response and response.status_code == 200 else None
    
    def get_repository_info(self, project_key: str, repository: str) -> Optional[Dict]:
        """Get repository information"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}"
        response = self._make_request('GET', endpoint)
        return response.json() if response and response.status_code == 200 else None
    
    # =============================================================================
    # BRANCH OPERATIONS
    # =============================================================================
    
    def list_branches(self, project_key: str, repository: str, limit: int = 100) -> Optional[Dict]:
        """Get all branches in a repository"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/branches"
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.json() if response and response.status_code == 200 else None
    
    def create_branch(self, project_key: str, repository: str, branch_name: str, start_point: str) -> bool:
        """Create a new branch"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/branches"
        data = {
            "name": branch_name,
            "startPoint": f"refs/heads/{start_point}"
        }
        response = self._make_request('POST', endpoint, json=data)
        return response and response.status_code == 200
    
    def delete_branch(self, project_key: str, repository: str, branch_name: str) -> bool:
        """Delete a branch"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/branches/{branch_name}"
        response = self._make_request('DELETE', endpoint)
        return response and response.status_code == 204
    
    def list_tags(self, project_key: str, repository: str, limit: int = 100) -> Optional[Dict]:
        """Get all tags in a repository"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/tags"
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.json() if response and response.status_code == 200 else None
    
    def get_latest_tag(self, project_key: str, repository: str) -> Optional[Dict]:
        """Get the latest tag"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/tags"
        params = {'orderBy': 'MODIFICATION', 'limit': 1}
        response = self._make_request('GET', endpoint, params=params)
        return response.json() if response and response.status_code == 200 else None
    
    # =============================================================================
    # SEARCH OPERATIONS
    # =============================================================================
    
    def search_code_in_project(self, project_key: str, query: str, limit: int = 50) -> Optional[Dict]:
        """Search code across all repositories in a project"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/search/code"
        params = {'query': query, 'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.json() if response and response.status_code == 200 else None
    
    def search_code_in_repository(self, project_key: str, repository: str, query: str) -> Optional[Dict]:
        """Search code in a specific repository"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/search/code"
        params = {'query': query}
        response = self._make_request('GET', endpoint, params=params)
        return response.json() if response and response.status_code == 200 else None
    
    # =============================================================================
    # PULL REQUEST OPERATIONS
    # =============================================================================
    
    def create_pull_request(self, project_key: str, repository: str, title: str, 
                          source_branch: str, target_branch: str, description: str = "",
                          reviewers: List[str] = None) -> Optional[Dict]:
        """Create a pull request"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/pull-requests"
        data = {
            "title": title,
            "description": description,
            "fromRef": {"id": f"refs/heads/{source_branch}"},
            "toRef": {"id": f"refs/heads/{target_branch}"}
        }
        if reviewers:
            data["reviewers"] = [{"user": {"name": reviewer}} for reviewer in reviewers]
        
        response = self._make_request('POST', endpoint, json=data)
        return response.json() if response and response.status_code == 201 else None
    
    def list_pull_requests(self, project_key: str, repository: str, state: str = "OPEN", limit: int = 25) -> Optional[Dict]:
        """List pull requests"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/pull-requests"
        params = {'state': state, 'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.json() if response and response.status_code == 200 else None
    
    def get_pull_request(self, project_key: str, repository: str, pr_id: str) -> Optional[Dict]:
        """Get pull request details"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}"
        response = self._make_request('GET', endpoint)
        return response.json() if response and response.status_code == 200 else None
    
    def get_pull_request_diff(self, project_key: str, repository: str, pr_id: str) -> Optional[str]:
        """Get pull request diff"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/diff"
        response = self._make_request('GET', endpoint)
        return response.text if response and response.status_code == 200 else None
    
    def get_pull_request_comments(self, project_key: str, repository: str, pr_id: str) -> Optional[Dict]:
        """Get pull request comments"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/comments"
        response = self._make_request('GET', endpoint)
        return response.json() if response and response.status_code == 200 else None
    
    def add_pull_request_comment(self, project_key: str, repository: str, pr_id: str, comment_text: str) -> Optional[Dict]:
        """Add a general comment to a pull request"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/comments"
        data = {"text": comment_text}
        response = self._make_request('POST', endpoint, json=data)
        return response.json() if response and response.status_code == 201 else None
    
    def add_inline_comment(self, project_key: str, repository: str, pr_id: str, 
                         comment_text: str, file_path: str, line: int,
                         from_hash: str, to_hash: str) -> Optional[Dict]:
        """Add an inline comment to a pull request"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/comments"
        data = {
            "text": comment_text,
            "anchor": {
                "diffType": "EFFECTIVE",
                "fromHash": from_hash,
                "toHash": to_hash,
                "path": file_path,
                "line": line,
                "lineType": "ADDED"
            }
        }
        response = self._make_request('POST', endpoint, json=data)
        return response.json() if response and response.status_code == 201 else None
    
    # =============================================================================
    # COMMIT OPERATIONS
    # =============================================================================
    
    def get_commits(self, project_key: str, repository: str, limit: int = 25) -> Optional[Dict]:
        """Get commits from a repository"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/commits"
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.json() if response and response.status_code == 200 else None
    
    def get_file_content(self, project_key: str, repository: str, file_path: str, branch: str = "main") -> Optional[str]:
        """Get file content from repository"""
        endpoint = f"/rest/api/1.0/projects/{project_key}/repos/{repository}/raw/{file_path}"
        params = {'at': f"refs/heads/{branch}"}
        response = self._make_request('GET', endpoint, params=params)
        return response.text if response and response.status_code == 200 else None

# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_repository_operations(api: BitbucketServerAPI):
    """Test repository-related operations"""
    print("\n" + "="*50)
    print("TESTING REPOSITORY OPERATIONS")
    print("="*50)
    
    # List repositories
    print("\n--- Testing list_repositories ---")
    repos = api.list_repositories(PROJECT_KEY)
    
    # Get repository info
    print("\n--- Testing get_repository_info ---")
    repo_info = api.get_repository_info(PROJECT_KEY, REPOSITORY_NAME)

def test_branch_operations(api: BitbucketServerAPI):
    """Test branch-related operations"""
    print("\n" + "="*50)
    print("TESTING BRANCH OPERATIONS")
    print("="*50)
    
    # List branches
    print("\n--- Testing list_branches ---")
    branches = api.list_branches(PROJECT_KEY, REPOSITORY_NAME)
    
    # List tags
    print("\n--- Testing list_tags ---")
    tags = api.list_tags(PROJECT_KEY, REPOSITORY_NAME)
    
    # Get latest tag
    print("\n--- Testing get_latest_tag ---")
    latest_tag = api.get_latest_tag(PROJECT_KEY, REPOSITORY_NAME)
    
    # Create branch (commented out to avoid creating test branches)
    # print("\n--- Testing create_branch ---")
    # api.create_branch(PROJECT_KEY, REPOSITORY_NAME, TEST_BRANCH_NAME, TEST_BASE_BRANCH)
    
    # Delete branch (commented out to avoid deleting branches)
    # print("\n--- Testing delete_branch ---")
    # api.delete_branch(PROJECT_KEY, REPOSITORY_NAME, TEST_BRANCH_NAME)

def test_search_operations(api: BitbucketServerAPI):
    """Test search-related operations"""
    print("\n" + "="*50)
    print("TESTING SEARCH OPERATIONS")
    print("="*50)
    
    # Search code in project
    print("\n--- Testing search_code_in_project ---")
    project_search = api.search_code_in_project(PROJECT_KEY, TEST_SEARCH_QUERY)
    
    # Search code in repository
    print("\n--- Testing search_code_in_repository ---")
    repo_search = api.search_code_in_repository(PROJECT_KEY, REPOSITORY_NAME, TEST_SEARCH_QUERY)

def test_pull_request_operations(api: BitbucketServerAPI):
    """Test pull request-related operations"""
    print("\n" + "="*50)
    print("TESTING PULL REQUEST OPERATIONS")
    print("="*50)
    
    # List pull requests
    print("\n--- Testing list_pull_requests ---")
    prs = api.list_pull_requests(PROJECT_KEY, REPOSITORY_NAME)
    
    # Get pull request details
    print("\n--- Testing get_pull_request ---")
    pr_details = api.get_pull_request(PROJECT_KEY, REPOSITORY_NAME, TEST_PR_ID)
    
    # Get pull request diff
    print("\n--- Testing get_pull_request_diff ---")
    pr_diff = api.get_pull_request_diff(PROJECT_KEY, REPOSITORY_NAME, TEST_PR_ID)
    
    # Get pull request comments
    print("\n--- Testing get_pull_request_comments ---")
    pr_comments = api.get_pull_request_comments(PROJECT_KEY, REPOSITORY_NAME, TEST_PR_ID)
    
    # Create pull request (commented out to avoid creating test PRs)
    # print("\n--- Testing create_pull_request ---")
    # api.create_pull_request(PROJECT_KEY, REPOSITORY_NAME, "Test PR", 
    #                        TEST_BRANCH_NAME, TEST_BASE_BRANCH, "Test PR description")
    
    # Add comment (commented out to avoid adding test comments)
    # print("\n--- Testing add_pull_request_comment ---")
    # api.add_pull_request_comment(PROJECT_KEY, REPOSITORY_NAME, TEST_PR_ID, "Test comment")

def test_commit_operations(api: BitbucketServerAPI):
    """Test commit-related operations"""
    print("\n" + "="*50)
    print("TESTING COMMIT OPERATIONS")
    print("="*50)
    
    # Get commits
    print("\n--- Testing get_commits ---")
    commits = api.get_commits(PROJECT_KEY, REPOSITORY_NAME)
    
    # Get file content
    print("\n--- Testing get_file_content ---")
    file_content = api.get_file_content(PROJECT_KEY, REPOSITORY_NAME, TEST_FILE_PATH)

def main():
    """Main test function"""
    print("Bitbucket Server REST API Test Script")
    print("=====================================")
    
    # Validate configuration
    if not all([BASE_URL != "https://your-bitbucket-server.company.com",
                PROJECT_KEY != "YOUR_PROJECT",
                REPOSITORY_NAME != "your-repository-name",
                PERSONAL_ACCESS_TOKEN != "your-personal-access-token"]):
        print("\n❌ ERROR: Please update the configuration variables at the top of the script!")
        print("   - BASE_URL: Your Bitbucket Server URL")
        print("   - PROJECT_KEY: Your project key")
        print("   - REPOSITORY_NAME: Repository name to test with")
        print("   - PERSONAL_ACCESS_TOKEN: Your personal access token")
        sys.exit(1)
    
    print(f"\nConfiguration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Project: {PROJECT_KEY}")
    print(f"  Repository: {REPOSITORY_NAME}")
    print(f"  Token: {'*' * (len(PERSONAL_ACCESS_TOKEN) - 4) + PERSONAL_ACCESS_TOKEN[-4:]}")
    
    # Initialize API client
    api = BitbucketServerAPI(BASE_URL, PERSONAL_ACCESS_TOKEN)
    
    # Run tests
    try:
        test_repository_operations(api)
        test_branch_operations(api)
        test_search_operations(api)
        test_pull_request_operations(api)
        test_commit_operations(api)
        
        print("\n" + "="*50)
        print("✅ ALL TESTS COMPLETED")
        print("="*50)
        print("\nReview the output above to check which APIs are working.")
        print("Update the configuration variables and uncomment write operations to test them.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
