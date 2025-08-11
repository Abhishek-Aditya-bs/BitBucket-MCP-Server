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
    
    def get_pull_request_diff(self, project_key: str, repository: str, pr_id: str, show_code_changes: bool = False) -> Optional[Dict]:
        """Get pull request diff - returns formatted diff summary for LLM analysis"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/diff"
        response = self._make_request('GET', endpoint)
        
        if response and response.status_code == 200:
            diff_text = response.text
            lines = diff_text.split('\n')
            
            # Parse diff to extract meaningful information
            files_changed = []
            current_file = None
            additions = 0
            deletions = 0
            
            for line in lines:
                if line.startswith('diff --git'):
                    # Extract file path from: diff --git a/path/file.ext b/path/file.ext
                    parts = line.split(' ')
                    if len(parts) >= 4:
                        file_path = parts[2][2:]  # Remove 'a/' prefix
                        current_file = {
                            'path': file_path,
                            'additions': 0,
                            'deletions': 0,
                            'type': 'modified'
                        }
                        files_changed.append(current_file)
                elif line.startswith('new file mode'):
                    if current_file:
                        current_file['type'] = 'added'
                elif line.startswith('deleted file mode'):
                    if current_file:
                        current_file['type'] = 'deleted'
                elif line.startswith('+') and not line.startswith('+++'):
                    # Count actual additions (not metadata lines)
                    additions += 1
                    if current_file:
                        current_file['additions'] += 1
                elif line.startswith('-') and not line.startswith('---'):
                    # Count actual deletions (not metadata lines)
                    deletions += 1
                    if current_file:
                        current_file['deletions'] += 1
            
            # Create summary for LLM consumption
            summary = {
                'total_files': len(files_changed),
                'total_additions': additions,
                'total_deletions': deletions,
                'files': files_changed,
                'diff_size': len(diff_text),
                'large_pr': len(diff_text) > 100000  # Consider >100KB as large
            }
            
            print(f"\n📊 Pull Request Diff Analysis:")
            print(f"   📁 Files changed: {summary['total_files']}")
            print(f"   ➕ Lines added: {summary['total_additions']}")
            print(f"   ➖ Lines deleted: {summary['total_deletions']}")
            print(f"   📏 Total diff size: {summary['diff_size']:,} characters")
            
            if summary['large_pr']:
                print(f"   ⚠️  Large PR detected - providing summary only")
            
            print(f"\n📝 File Changes:")
            for i, file in enumerate(files_changed[:10], 1):  # Show max 10 files
                change_type = {'added': '🆕', 'deleted': '🗑️', 'modified': '✏️'}
                print(f"   {i}. {change_type.get(file['type'], '✏️')} {file['path']}")
                print(f"      +{file['additions']} -{file['deletions']} lines")
            
            if len(files_changed) > 10:
                print(f"   ... and {len(files_changed) - 10} more files")
            
            # Optionally show actual code changes for small PRs
            if show_code_changes and not summary['large_pr']:
                print(f"\n📋 Code Changes Preview:")
                print(f"   (Showing first 2000 characters of actual diff)")
                print(f"   {'-'*50}")
                print(f"{diff_text[:2000]}")
                if len(diff_text) > 2000:
                    print(f"   ... (truncated - total {len(diff_text):,} characters)")
                print(f"   {'-'*50}")
                
            return summary
        return None
    
    def get_pr_for_code_review(self, project_key: str, repository: str, pr_id: str) -> Optional[Dict]:
        """Get PR diff optimized specifically for LLM code review - shows actual code changes"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/diff"
        response = self._make_request('GET', endpoint)
        
        if response and response.status_code == 200:
            diff_text = response.text
            lines = diff_text.split('\n')
            
            # Parse diff to extract actual code changes for review
            files_for_review = []
            current_file = None
            current_hunk = None
            
            for line in lines:
                if line.startswith('diff --git'):
                    # Save previous file
                    if current_file and current_file['hunks']:
                        files_for_review.append(current_file)
                    
                    # Start new file
                    parts = line.split(' ')
                    file_path = parts[2][2:] if len(parts) >= 4 else 'unknown'
                    current_file = {
                        'file_path': file_path,
                        'file_type': 'modified',
                        'hunks': [],
                        'total_additions': 0,
                        'total_deletions': 0
                    }
                    current_hunk = None
                    
                elif line.startswith('new file mode'):
                    if current_file:
                        current_file['file_type'] = 'added'
                elif line.startswith('deleted file mode'):
                    if current_file:
                        current_file['file_type'] = 'deleted'
                elif line.startswith('@@') and current_file:
                    # New hunk - save previous one
                    if current_hunk:
                        current_file['hunks'].append(current_hunk)
                    
                    # Parse hunk header: @@ -42,7 +42,10 @@ method signature
                    current_hunk = {
                        'header': line,
                        'changes': [],
                        'additions': 0,
                        'deletions': 0
                    }
                elif current_hunk and (line.startswith('+') or line.startswith('-') or line.startswith(' ')):
                    # Actual code changes
                    if line.startswith('+') and not line.startswith('+++'):
                        current_hunk['changes'].append(('added', line[1:]))
                        current_hunk['additions'] += 1
                        current_file['total_additions'] += 1
                    elif line.startswith('-') and not line.startswith('---'):
                        current_hunk['changes'].append(('removed', line[1:]))
                        current_hunk['deletions'] += 1
                        current_file['total_deletions'] += 1
                    elif line.startswith(' '):
                        current_hunk['changes'].append(('context', line[1:]))
            
            # Save final hunk and file
            if current_hunk:
                current_file['hunks'].append(current_hunk)
            if current_file and current_file['hunks']:
                files_for_review.append(current_file)
            
            # Calculate total changes
            total_files = len(files_for_review)
            total_additions = sum(f['total_additions'] for f in files_for_review)
            total_deletions = sum(f['total_deletions'] for f in files_for_review)
            
            # Determine review strategy based on size
            is_large_pr = len(diff_text) > 50000  # 50KB threshold for detailed review
            
            print(f"\n📋 Code Review Analysis:")
            print(f"   📁 Files to review: {total_files}")
            print(f"   ➕ Lines added: {total_additions}")
            print(f"   ➖ Lines deleted: {total_deletions}")
            print(f"   📏 Diff size: {len(diff_text):,} characters")
            
            if is_large_pr:
                print(f"   ⚠️  Large PR - showing key changes only")
                # For large PRs, show only files with significant changes
                files_for_review = [f for f in files_for_review if f['total_additions'] + f['total_deletions'] > 10]
                files_for_review = files_for_review[:5]  # Max 5 files for large PRs
            else:
                print(f"   ✅ Normal size PR - showing detailed changes")
                files_for_review = files_for_review[:8]  # Max 8 files for normal PRs
            
            print(f"\n🔍 Code Changes for Review:")
            
            for i, file_info in enumerate(files_for_review, 1):
                file_type_icon = {'added': '🆕', 'deleted': '🗑️', 'modified': '✏️'}
                print(f"\n   {i}. {file_type_icon.get(file_info['file_type'], '✏️')} {file_info['file_path']}")
                print(f"      Changes: +{file_info['total_additions']} -{file_info['total_deletions']} lines")
                
                # Show actual code changes for each file
                for j, hunk in enumerate(file_info['hunks'][:3], 1):  # Max 3 hunks per file
                    print(f"\n      📍 Hunk {j}: {hunk['header']}")
                    
                    # Show the actual code changes (limited for context)
                    lines_shown = 0
                    context_lines = 0
                    
                    for change_type, code_line in hunk['changes']:
                        if lines_shown >= 25:  # Max 25 lines per hunk
                            remaining = len(hunk['changes']) - lines_shown
                            print(f"         ... ({remaining} more lines in this hunk)")
                            break
                        
                        if change_type == 'added':
                            print(f"      ➕  {code_line}")
                            lines_shown += 1
                        elif change_type == 'removed':
                            print(f"      ➖  {code_line}")
                            lines_shown += 1
                        elif change_type == 'context' and context_lines < 3:  # Limit context
                            print(f"          {code_line}")
                            context_lines += 1
                            lines_shown += 1
                
                if len(file_info['hunks']) > 3:
                    print(f"      ... and {len(file_info['hunks']) - 3} more hunks")
            
            if len([f for f in files_for_review if f['total_additions'] + f['total_deletions'] > 0]) < total_files:
                remaining = total_files - len(files_for_review)
                print(f"\n   ... and {remaining} more files (smaller changes)")
            
            return {
                'files': files_for_review,
                'total_files': total_files,
                'total_additions': total_additions,
                'total_deletions': total_deletions,
                'diff_size': len(diff_text),
                'review_strategy': 'detailed' if not is_large_pr else 'focused',
                'ready_for_llm_review': True
            }
        return None
    
    def get_detailed_file_changes(self, project_key: str, repository: str, pr_id: str, max_files: int = 3) -> Optional[Dict]:
        """Get detailed code changes for specific files - shows actual code modifications"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/diff"
        response = self._make_request('GET', endpoint)
        
        if response and response.status_code == 200:
            diff_text = response.text
            lines = diff_text.split('\n')
            
            # Parse diff into file sections with actual code changes
            file_sections = []
            current_section = None
            
            for line in lines:
                if line.startswith('diff --git'):
                    # Start new file section
                    if current_section:
                        file_sections.append(current_section)
                    
                    parts = line.split(' ')
                    file_path = parts[2][2:] if len(parts) >= 4 else 'unknown'
                    current_section = {
                        'file_path': file_path,
                        'changes': [],
                        'context': []
                    }
                elif current_section:
                    if line.startswith('@@'):
                        # Hunk header - shows line numbers
                        current_section['context'].append(line)
                    elif line.startswith('+') and not line.startswith('+++'):
                        current_section['changes'].append(('added', line[1:]))
                    elif line.startswith('-') and not line.startswith('---'):
                        current_section['changes'].append(('removed', line[1:]))
                    elif line.startswith(' '):
                        # Context line
                        current_section['changes'].append(('context', line[1:]))
            
            # Add final section
            if current_section:
                file_sections.append(current_section)
            
            print(f"\n🔍 Detailed Code Changes (showing up to {max_files} files):")
            
            for i, section in enumerate(file_sections[:max_files], 1):
                print(f"\n   📄 {i}. {section['file_path']}")
                
                # Show hunk context
                for context in section['context'][:2]:  # Max 2 hunks
                    print(f"      📍 {context}")
                
                # Show actual changes (limited)
                changes_shown = 0
                for change_type, content in section['changes']:
                    if changes_shown >= 20:  # Max 20 lines per file
                        remaining = len(section['changes']) - changes_shown
                        print(f"      ... ({remaining} more lines)")
                        break
                        
                    if change_type == 'added':
                        print(f"      ➕ {content}")
                    elif change_type == 'removed':
                        print(f"      ➖ {content}")
                    elif change_type == 'context' and changes_shown < 15:  # Show less context
                        print(f"         {content}")
                    
                    changes_shown += 1
            
            if len(file_sections) > max_files:
                print(f"\n   ... and {len(file_sections) - max_files} more files with changes")
            
            return {
                'file_sections': file_sections,
                'total_files': len(file_sections),
                'detailed_view': True
            }
        return None
    
    def get_pull_request_comments(self, project_key: str, repository: str, pr_id: str) -> Optional[List[Dict]]:
        """Get pull request comments - returns detailed formatted comment list with file locations"""
        endpoint = f"/rest/api/latest/projects/{project_key}/repos/{repository}/pull-requests/{pr_id}/activities"
        params = {'fromType': 'COMMENT'}
        response = self._make_request('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            data = response.json()
            comments = []
            general_comments = 0
            inline_comments = 0
            
            for activity in data.get('values', []):
                if activity.get('action') == 'COMMENTED':
                    comment_data = activity.get('comment', {})
                    anchor = comment_data.get('anchor')
                    
                    # Determine comment type and extract location info
                    is_inline = bool(anchor)
                    if is_inline:
                        inline_comments += 1
                    else:
                        general_comments += 1
                    
                    comment_info = {
                        'id': comment_data.get('id'),
                        'text': comment_data.get('text', ''),
                        'author': comment_data.get('author', {}).get('displayName'),
                        'created_date': comment_data.get('createdDate', 0) // 1000 if comment_data.get('createdDate') else 0,
                        'type': 'inline' if is_inline else 'general',
                        'file_path': anchor.get('path') if anchor else None,
                        'line_number': anchor.get('line') if anchor else None,
                        'line_type': anchor.get('lineType') if anchor else None,  # ADDED, REMOVED, CONTEXT
                        'from_hash': anchor.get('fromHash', '')[:8] if anchor else None,
                        'to_hash': anchor.get('toHash', '')[:8] if anchor else None
                    }
                    
                    # Truncate long comments for display
                    display_text = comment_info['text']
                    if len(display_text) > 150:
                        display_text = display_text[:150] + '...'
                    comment_info['display_text'] = display_text
                    
                    comments.append(comment_info)
            
            # Sort comments: inline comments first, then general comments
            comments.sort(key=lambda x: (x['type'] == 'general', x['file_path'] or '', x['line_number'] or 0))
            
            print(f"\n💬 Found {len(comments)} comments ({inline_comments} inline, {general_comments} general):")
            
            # Group and display inline comments by file
            current_file = None
            for i, comment in enumerate(comments, 1):
                if comment['type'] == 'inline':
                    if comment['file_path'] != current_file:
                        current_file = comment['file_path']
                        print(f"\n   📄 {current_file}:")
                    
                    line_indicator = {
                        'ADDED': '➕',
                        'REMOVED': '➖', 
                        'CONTEXT': '📍'
                    }.get(comment['line_type'], '📍')
                    
                    print(f"      {line_indicator} Line {comment['line_number']} - {comment['author']}")
                    print(f"         💭 {comment['display_text']}")
                    
                else:  # General comments
                    if current_file is not None:  # Add separator after inline comments
                        print(f"\n   💬 General Comments:")
                        current_file = None
                    print(f"      {i}. {comment['author']}")
                    print(f"         💭 {comment['display_text']}")
            
            # Return structured data for LLM analysis
            return {
                'total_comments': len(comments),
                'inline_comments': inline_comments,
                'general_comments': general_comments,
                'comments': comments,
                'files_with_comments': list(set([c['file_path'] for c in comments if c['file_path']]))
            }
        return None
    
    def get_pr_summary_for_llm(self, project_key: str, repository: str, pr_id: str) -> Optional[Dict]:
        """Get comprehensive PR summary optimized for LLM analysis"""
        print(f"\n🔍 Generating comprehensive PR summary for LLM analysis...")
        
        # Get PR details, code changes, and comments for comprehensive review
        pr_details = self.get_pull_request(project_key, repository, pr_id)
        pr_code_changes = self.get_pr_for_code_review(project_key, repository, pr_id)  
        pr_comments = self.get_pull_request_comments(project_key, repository, pr_id)
        
        if not pr_details:
            return None
            
        summary = {
            'pr_info': pr_details,
            'code_changes': pr_code_changes,
            'comments': pr_comments,
            'analysis_ready': True
        }
        
        # Add recommendations for LLM
        if pr_code_changes and pr_code_changes.get('review_strategy') == 'focused':
            summary['llm_guidance'] = {
                'focus_areas': ['major_modifications', 'key_files'],
                'review_strategy': 'focused',
                'attention_files': [f['file_path'] for f in pr_code_changes['files'][:5] if f['total_additions'] + f['total_deletions'] > 20]
            }
        else:
            summary['llm_guidance'] = {
                'focus_areas': ['line_level_changes', 'detailed_review', 'code_quality'],
                'review_strategy': 'comprehensive',
                'attention_files': [f['file_path'] for f in pr_code_changes['files'] if f['total_additions'] + f['total_deletions'] > 5] if pr_code_changes else []
            }
        
        print(f"\n📋 LLM Analysis Summary Generated:")
        print(f"   🎯 Review Strategy: {summary['llm_guidance']['review_strategy']}")
        print(f"   🔍 Focus Areas: {', '.join(summary['llm_guidance']['focus_areas'])}")
        if summary['llm_guidance']['attention_files']:
            print(f"   📂 Key Files: {', '.join(summary['llm_guidance']['attention_files'][:3])}{'...' if len(summary['llm_guidance']['attention_files']) > 3 else ''}")
        
        return summary
    
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
    
    # Get pull request diff (summary only)
    print("\n--- Testing get_pull_request_diff (summary) ---")
    pr_diff = api.get_pull_request_diff(PROJECT_KEY, REPOSITORY_NAME, TEST_PR_ID)
    
    # Get detailed code changes (actual code)
    print("\n--- Testing get_detailed_file_changes (actual code) ---")
    detailed_changes = api.get_detailed_file_changes(PROJECT_KEY, REPOSITORY_NAME, TEST_PR_ID)
    
    # Get PR optimized for LLM code review (RECOMMENDED FOR AI)
    print("\n--- Testing get_pr_for_code_review (LLM-optimized) ---")
    code_review_data = api.get_pr_for_code_review(PROJECT_KEY, REPOSITORY_NAME, TEST_PR_ID)
    
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
    
    # Get comprehensive LLM-ready PR summary
    print("\n--- Testing get_pr_summary_for_llm ---")
    pr_summary = api.get_pr_summary_for_llm(PROJECT_KEY, REPOSITORY_NAME, TEST_PR_ID)

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
