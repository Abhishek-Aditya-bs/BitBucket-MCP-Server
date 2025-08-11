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
TEST_PR_ID = "1"
TEST_COMMIT_MESSAGE = "Test commit message"

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
            print(f"\n🌐 {method} {endpoint}")
            print(f"📊 Status: {response.status_code}")
            
            # For debugging: show abbreviated response
            if response.status_code >= 400:
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        error_data = response.json()
                        print(f"❌ Error: {error_data}")
                    except:
                        print(f"❌ Error: {response.text[:200]}...")
                else:
                    print(f"❌ Error: {response.text[:200]}...")
            else:
                print(f"✅ Success - Data will be formatted below")
            
            return response
        except Exception as e:
            print(f"💥 Request failed: {e}")
            return None
    
    # =============================================================================
    # REPOSITORY OPERATIONS
    # =============================================================================
    
    def list_repositories(self, project_key: str, limit: int = 100) -> Optional[List[Dict]]:
        """List all repositories in a project - returns formatted repository info"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos"
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            repos = []
            for repo in data.get('values', []):
                repo_info = {
                    'slug': repo.get('slug'),
                    'name': repo.get('name'),
                    'description': repo.get('description', 'No description'),
                    'state': repo.get('state'),
                    'public': repo.get('public', False)
                }
                repos.append(repo_info)
            
            print(f"\n📁 Found {len(repos)} repositories:")
            for repo in repos:
                print(f"   • {repo['slug']} - {repo['name']} ({repo['state']})")
                if repo['description'] != 'No description':
                    print(f"     Description: {repo['description'][:100]}...")
            return repos
        return None
    
    def get_repository_info(self, project_key: str, repository: str) -> Optional[Dict]:
        """Get repository information - returns formatted repo details"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}"
        response = self._make_request('GET', endpoint)
        
        if response and response.status_code == 200:
            data = response.json()
            repo_info = {
                'slug': data.get('slug'),
                'name': data.get('name'),
                'description': data.get('description', 'No description'),
                'state': data.get('state'),
                'public': data.get('public', False),
                'clone_url': next((link['href'] for link in data.get('links', {}).get('clone', []) 
                                 if link.get('name') == 'http'), 'N/A')
            }
            
            print(f"\n📄 Repository Details:")
            print(f"   Name: {repo_info['name']}")
            print(f"   Slug: {repo_info['slug']}")
            print(f"   State: {repo_info['state']}")
            print(f"   Public: {repo_info['public']}")
            print(f"   Clone URL: {repo_info['clone_url']}")
            if repo_info['description'] != 'No description':
                print(f"   Description: {repo_info['description']}")
            return repo_info
        return None
    
    # =============================================================================
    # BRANCH OPERATIONS
    # =============================================================================
    
    def list_branches(self, project_key: str, repository: str, limit: int = 100) -> Optional[List[Dict]]:
        """Get all branches in a repository - returns formatted branch info"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/branches"
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            branches = []
            for branch in data.get('values', []):
                branch_info = {
                    'name': branch.get('displayId'),
                    'id': branch.get('id'),
                    'is_default': branch.get('isDefault', False),
                    'latest_commit': branch.get('latestCommit', '')[:8] if branch.get('latestCommit') else 'N/A'
                }
                branches.append(branch_info)
            
            print(f"\n🌿 Found {len(branches)} branches:")
            for branch in branches:
                default_marker = " (default)" if branch['is_default'] else ""
                print(f"   • {branch['name']}{default_marker} - Commit: {branch['latest_commit']}")
            return branches
        return None
    
    def create_branch(self, project_key: str, repository: str, branch_name: str, start_point: str) -> bool:
        """Create a new branch"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/branches"
        data = {
            "name": branch_name,
            "startPoint": f"refs/heads/{start_point}"
        }
        response = self._make_request('POST', endpoint, json=data)
        success = response and response.status_code == 200
        if success:
            print(f"\n✅ Branch '{branch_name}' created successfully from '{start_point}'")
        else:
            print(f"\n❌ Failed to create branch '{branch_name}'")
        return success
    
    def delete_branch(self, project_key: str, repository: str, branch_name: str) -> bool:
        """Delete a branch"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/branches/{branch_name}"
        response = self._make_request('DELETE', endpoint)
        success = response and response.status_code == 204
        if success:
            print(f"\n✅ Branch '{branch_name}' deleted successfully")
        else:
            print(f"\n❌ Failed to delete branch '{branch_name}'")
        return success
    
    def get_latest_tag(self, project_key: str, repository: str) -> Optional[str]:
        """Get the latest tag name"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/tags"
        params = {'orderBy': 'MODIFICATION', 'limit': 1}
        response = self._make_request('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            tags = data.get('values', [])
            if tags:
                latest_tag = tags[0]['displayId']
                latest_commit = tags[0].get('latestCommit', '')[:8] if tags[0].get('latestCommit') else 'N/A'
                print(f"\n🏷️ Latest Tag: {latest_tag}")
                print(f"   Commit: {latest_commit}")
                return latest_tag
            else:
                print(f"\n🏷️ No tags found in repository")
        return None
    

    
    # =============================================================================
    # PULL REQUEST OPERATIONS
    # =============================================================================
    
    def create_pull_request(self, project_key: str, repository: str, title: str, 
                          source_branch: str, target_branch: str, description: str = "",
                          reviewers: List[str] = None) -> Optional[Dict]:
        """Create a pull request - returns formatted PR info"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests"
        data = {
            "title": title,
            "description": description,
            "fromRef": {"id": f"refs/heads/{source_branch}"},
            "toRef": {"id": f"refs/heads/{target_branch}"}
        }
        if reviewers:
            data["reviewers"] = [{"user": {"name": reviewer}} for reviewer in reviewers]
        
        response = self._make_request('POST', endpoint, json=data)
        
        if response and response.status_code == 201:
            pr_data = response.json()
            pr_info = {
                'id': pr_data.get('id'),
                'title': pr_data.get('title'),
                'state': pr_data.get('state'),
                'source_branch': pr_data.get('fromRef', {}).get('displayId'),
                'target_branch': pr_data.get('toRef', {}).get('displayId'),
                'author': pr_data.get('author', {}).get('user', {}).get('displayName'),
                'url': pr_data.get('links', {}).get('self', [{}])[0].get('href', 'N/A')
            }
            
            print(f"\n✅ Pull Request Created:")
            print(f"   ID: #{pr_info['id']}")
            print(f"   Title: {pr_info['title']}")
            print(f"   From: {pr_info['source_branch']} → {pr_info['target_branch']}")
            print(f"   Author: {pr_info['author']}")
            print(f"   State: {pr_info['state']}")
            return pr_info
        return None
    
    def list_pull_requests(self, project_key: str, repository: str, state: str = "OPEN", limit: int = 25) -> Optional[List[Dict]]:
        """List pull requests - returns formatted PR list"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests"
        params = {'state': state, 'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            prs = []
            for pr in data.get('values', []):
                pr_info = {
                    'id': pr.get('id'),
                    'title': pr.get('title'),
                    'state': pr.get('state'),
                    'source_branch': pr.get('fromRef', {}).get('displayId'),
                    'target_branch': pr.get('toRef', {}).get('displayId'),
                    'author': pr.get('author', {}).get('user', {}).get('displayName'),
                    'created_date': pr.get('createdDate', 0) // 1000 if pr.get('createdDate') else 0,  # Convert to seconds
                    'reviewer_count': len(pr.get('reviewers', []))
                }
                prs.append(pr_info)
            
            print(f"\n📋 Found {len(prs)} {state.lower()} pull requests:")
            for pr in prs:
                print(f"   • #{pr['id']} - {pr['title']}")
                print(f"     From: {pr['source_branch']} → {pr['target_branch']}")
                print(f"     Author: {pr['author']} | Reviewers: {pr['reviewer_count']} | State: {pr['state']}")
            return prs
        return None
    
    def get_pull_request(self, project_key: str, repository: str, pr_id: str) -> Optional[Dict]:
        """Get pull request details - returns formatted PR details"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}"
        response = self._make_request('GET', endpoint)
        
        if response and response.status_code == 200:
            pr = response.json()
            pr_info = {
                'id': pr.get('id'),
                'title': pr.get('title'),
                'description': pr.get('description', 'No description'),
                'state': pr.get('state'),
                'source_branch': pr.get('fromRef', {}).get('displayId'),
                'target_branch': pr.get('toRef', {}).get('displayId'),
                'author': pr.get('author', {}).get('user', {}).get('displayName'),
                'created_date': pr.get('createdDate', 0) // 1000 if pr.get('createdDate') else 0,
                'reviewers': [r.get('user', {}).get('displayName') for r in pr.get('reviewers', [])],
                'url': pr.get('links', {}).get('self', [{}])[0].get('href', 'N/A')
            }
            
            print(f"\n📄 Pull Request #{pr_info['id']} Details:")
            print(f"   Title: {pr_info['title']}")
            print(f"   State: {pr_info['state']}")
            print(f"   From: {pr_info['source_branch']} → {pr_info['target_branch']}")
            print(f"   Author: {pr_info['author']}")
            print(f"   Reviewers: {', '.join(pr_info['reviewers']) if pr_info['reviewers'] else 'None'}")
            if pr_info['description'] != 'No description':
                print(f"   Description: {pr_info['description'][:100]}...")
            return pr_info
        return None
    
    def get_pull_request_diff(self, project_key: str, repository: str, pr_id: str) -> Optional[str]:
        """Get pull request diff - returns formatted diff summary"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/diff"
        response = self._make_request('GET', endpoint)
        
        if response and response.status_code == 200:
            diff_text = response.text
            lines = diff_text.split('\n')
            
            # Count file changes and modifications
            files_changed = len([line for line in lines if line.startswith('diff --git')])
            additions = len([line for line in lines if line.startswith('+')])
            deletions = len([line for line in lines if line.startswith('-')])
            
            print(f"\n📊 Pull Request Diff Summary:")
            print(f"   Files changed: {files_changed}")
            print(f"   Lines added: {additions}")
            print(f"   Lines deleted: {deletions}")
            print(f"   Total diff size: {len(diff_text)} characters")
            
            return diff_text
        return None
    
    def get_pull_request_comments(self, project_key: str, repository: str, pr_id: str) -> Optional[List[Dict]]:
        """Get pull request comments - returns formatted comment list"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/activities"
        params = {'fromType': 'COMMENT'}
        response = self._make_request('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            comments = []
            for activity in data.get('values', []):
                if activity.get('action') == 'COMMENTED':
                    comment_data = activity.get('comment', {})
                    comment_info = {
                        'id': comment_data.get('id'),
                        'text': comment_data.get('text', '')[:200] + '...' if len(comment_data.get('text', '')) > 200 else comment_data.get('text', ''),
                        'author': comment_data.get('author', {}).get('displayName'),
                        'created_date': comment_data.get('createdDate', 0) // 1000 if comment_data.get('createdDate') else 0,
                        'file_path': comment_data.get('anchor', {}).get('path') if comment_data.get('anchor') else None,
                        'line': comment_data.get('anchor', {}).get('line') if comment_data.get('anchor') else None
                    }
                    comments.append(comment_info)
            
            print(f"\n💬 Found {len(comments)} comments:")
            for i, comment in enumerate(comments, 1):
                comment_type = "inline" if comment['file_path'] else "general"
                print(f"   {i}. [{comment_type.upper()}] {comment['author']}")
                print(f"      Text: {comment['text']}")
                if comment['file_path']:
                    print(f"      File: {comment['file_path']}:{comment['line']}")
            return comments
        return None
    
    def add_pull_request_comment(self, project_key: str, repository: str, pr_id: str, comment_text: str) -> Optional[Dict]:
        """Add a general comment to a pull request"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/comments"
        data = {"text": comment_text}
        response = self._make_request('POST', endpoint, json=data)
        
        if response and response.status_code == 201:
            comment_data = response.json()
            print(f"\n✅ Comment added successfully:")
            print(f"   ID: {comment_data.get('id')}")
            print(f"   Text: {comment_text[:100]}...")
            return comment_data
        return None
    
    def add_inline_comment(self, project_key: str, repository: str, pr_id: str, 
                         comment_text: str, file_path: str, line: int,
                         from_hash: str, to_hash: str) -> Optional[Dict]:
        """Add an inline comment to a pull request"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/comments"
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
        
        if response and response.status_code == 201:
            comment_data = response.json()
            print(f"\n✅ Inline comment added successfully:")
            print(f"   File: {file_path}:{line}")
            print(f"   Text: {comment_text[:100]}...")
            return comment_data
        return None
    
    # =============================================================================
    # COMMIT OPERATIONS
    # =============================================================================
    
    def get_commits(self, project_key: str, repository: str, limit: int = 25) -> Optional[List[Dict]]:
        """Get commits from a repository - returns formatted commit list"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/commits"
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            commits = []
            for commit in data.get('values', []):
                commit_info = {
                    'id': commit.get('id', '')[:8],  # Short hash
                    'full_id': commit.get('id', ''),
                    'message': commit.get('message', '').strip().split('\n')[0][:100] + '...' if len(commit.get('message', '').strip()) > 100 else commit.get('message', '').strip(),
                    'author': commit.get('author', {}).get('displayName'),
                    'author_email': commit.get('author', {}).get('emailAddress'),
                    'commit_date': commit.get('authorTimestamp', 0) // 1000 if commit.get('authorTimestamp') else 0,
                    'parent_count': len(commit.get('parents', []))
                }
                commits.append(commit_info)
            
            print(f"\n📝 Found {len(commits)} recent commits:")
            for i, commit in enumerate(commits, 1):
                print(f"   {i}. {commit['id']} - {commit['author']}")
                print(f"      Message: {commit['message']}")
                if commit['parent_count'] > 1:
                    print(f"      Type: Merge commit ({commit['parent_count']} parents)")
            return commits
        return None
    


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
    
    # Get latest tag
    print("\n--- Testing get_latest_tag ---")
    latest_tag = api.get_latest_tag(PROJECT_KEY, REPOSITORY_NAME)
    
    # Create branch (commented out to avoid creating test branches)
    # print("\n--- Testing create_branch ---")
    # api.create_branch(PROJECT_KEY, REPOSITORY_NAME, TEST_BRANCH_NAME, TEST_BASE_BRANCH)
    
    # Delete branch (commented out to avoid deleting branches)
    # print("\n--- Testing delete_branch ---")
    # api.delete_branch(PROJECT_KEY, REPOSITORY_NAME, TEST_BRANCH_NAME)



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
