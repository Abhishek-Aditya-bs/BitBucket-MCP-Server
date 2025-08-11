# Bitbucket MCP Server - Project Overview

## Executive Summary

The Bitbucket Model Context Protocol (MCP) Server is designed to streamline developer workflows by providing intelligent Git operations and code review capabilities through integration with our self-hosted Bitbucket Server instance. This MCP server will enable MCP-compatible AI assistants (such as Claude, GitHub Copilot, Cursor, and others) to interact directly with Bitbucket repositories, automating routine tasks and enhancing code quality through AI-assisted reviews.

## Project Scope

This MCP server focuses on core Git operations and intelligent code review workflows, specifically designed for our Bitbucket Server environment hosted in our data center. The solution leverages Bitbucket Server REST API endpoints and integrates seamlessly with MCP-compatible AI assistants for enhanced developer productivity.

## Core Use Cases

### 1. Branch Management
- Create feature, hotfix, and bugfix branches
- Create release branches from latest or specified tag versions
- Intelligent tag validation and confirmation for release branches
- Branch cleanup for stale branches (older than 3 months)

### 2. Cross-Repository Code Search
- Search for keywords and code snippets across all repositories in a project space
- File-level search results with context
- Multi-repository search capabilities

### 3. Intelligent Commit Operations
- Generate intelligent commit messages based on staged changes
- Pre-commit security vulnerability scanning
- Basic code quality checks before push
- Automated push operations

### 4. Pull Request Management
- Create pull requests with intelligent descriptions
- List and filter open pull requests by various criteria
- Retrieve detailed pull request information
- Advanced filtering capabilities (by author, date, repository, etc.)

### 5. AI-Assisted Code Review
- Extract pull request diffs and metadata
- Review pull requests against codebase context using AI assistants
- Address existing PR comments automatically
- Post review comments back to Bitbucket

## MCP Tools Specification

### Branch Operations

#### `create_branch`
```json
{
  "name": "create_branch",
  "description": "Create a new branch with specified type and base",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "repository": {"type": "string", "description": "Repository name"},
      "branch_name": {"type": "string", "description": "Name of the new branch"},
      "branch_type": {"type": "string", "enum": ["feature", "hotfix", "bugfix", "release"], "description": "Type of branch to create"},
      "base_ref": {"type": "string", "description": "Base branch or tag (optional, defaults to main/master)"}
    },
    "required": ["project_key", "repository", "branch_name", "branch_type"]
  }
}
```

#### `create_release_branch`
```json
{
  "name": "create_release_branch",
  "description": "Create a release branch from latest or specified tag",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "repository": {"type": "string", "description": "Repository name"},
      "branch_name": {"type": "string", "description": "Release branch name"},
      "tag_version": {"type": "string", "description": "Specific tag version (optional, uses latest if not provided)"},
      "confirm_latest": {"type": "boolean", "description": "Confirm creation from latest tag"}
    },
    "required": ["project_key", "repository", "branch_name"]
  }
}
```

#### `cleanup_old_branches`
```json
{
  "name": "cleanup_old_branches",
  "description": "Delete branches older than specified period",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "repository": {"type": "string", "description": "Repository name"},
      "age_threshold_days": {"type": "number", "description": "Age threshold in days", "default": 90},
      "dry_run": {"type": "boolean", "description": "Preview branches to be deleted", "default": true}
    },
    "required": ["project_key", "repository"]
  }
}
```

### Repository Operations

#### `list_repositories`
```json
{
  "name": "list_repositories",
  "description": "List all repositories in a project",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "limit": {"type": "number", "description": "Maximum number of results", "default": 100}
    },
    "required": ["project_key"]
  }
}
```

### Search Operations

#### `search_code`
```json
{
  "name": "search_code",
  "description": "Search for keywords across repositories in project space",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "query": {"type": "string", "description": "Search query (keywords or code snippets)"},
      "repository": {"type": "string", "description": "Specific repository (optional, searches all if not provided)"},
      "file_extensions": {"type": "array", "items": {"type": "string"}, "description": "Filter by file extensions"},
      "max_results": {"type": "number", "description": "Maximum number of results", "default": 50}
    },
    "required": ["project_key", "query"]
  }
}
```

### Commit Operations

#### `intelligent_commit`
```json
{
  "name": "intelligent_commit",
  "description": "Generate commit message and perform security scan before push",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "repository": {"type": "string", "description": "Repository name"},
      "commit_message": {"type": "string", "description": "Custom commit message (optional, auto-generated if not provided)"},
      "perform_security_scan": {"type": "boolean", "description": "Perform security scan before commit", "default": true},
      "auto_push": {"type": "boolean", "description": "Automatically push after commit", "default": false}
    },
    "required": ["project_key", "repository"]
  }
}
```

### Pull Request Operations

#### `create_pull_request`
```json
{
  "name": "create_pull_request",
  "description": "Create a pull request with intelligent description",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "repository": {"type": "string", "description": "Repository name"},
      "source_branch": {"type": "string", "description": "Source branch name"},
      "target_branch": {"type": "string", "description": "Target branch name"},
      "title": {"type": "string", "description": "PR title (optional, auto-generated if not provided)"},
      "description": {"type": "string", "description": "PR description (optional, auto-generated if not provided)"},
      "reviewers": {"type": "array", "items": {"type": "string"}, "description": "List of reviewer usernames"}
    },
    "required": ["project_key", "repository", "source_branch", "target_branch"]
  }
}
```

#### `list_pull_requests`
```json
{
  "name": "list_pull_requests",
  "description": "List and filter pull requests",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "repository": {"type": "string", "description": "Repository name (optional, searches all repositories if not provided)"},
      "state": {"type": "string", "enum": ["OPEN", "MERGED", "DECLINED", "ALL"], "description": "PR state filter", "default": "OPEN"},
      "author": {"type": "string", "description": "Filter by author username"},
      "target_branch": {"type": "string", "description": "Filter by target branch"},
      "created_after": {"type": "string", "description": "Filter PRs created after date (ISO 8601 format)"},
      "limit": {"type": "number", "description": "Maximum number of results", "default": 25}
    },
    "required": ["project_key"]
  }
}
```

#### `get_pull_request_info`
```json
{
  "name": "get_pull_request_info",
  "description": "Get detailed information about a specific pull request",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "repository": {"type": "string", "description": "Repository name"},
      "pr_id": {"type": "string", "description": "Pull request ID"}
    },
    "required": ["project_key", "repository", "pr_id"]
  }
}
```

### Code Review Operations

#### `review_pull_request`
```json
{
  "name": "review_pull_request",
  "description": "Perform AI-assisted code review using MCP-compatible AI assistants",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "repository": {"type": "string", "description": "Repository name"},
      "pr_id": {"type": "string", "description": "Pull request ID"},
      "review_focus": {"type": "array", "items": {"type": "string"}, "description": "Specific areas to focus on (security, performance, maintainability)"},
      "address_existing_comments": {"type": "boolean", "description": "Address existing PR comments", "default": true}
    },
    "required": ["project_key", "repository", "pr_id"]
  }
}
```

#### `get_pr_diff`
```json
{
  "name": "get_pr_diff",
  "description": "Extract pull request diff and metadata",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "repository": {"type": "string", "description": "Repository name"},
      "pr_id": {"type": "string", "description": "Pull request ID"},
      "include_comments": {"type": "boolean", "description": "Include existing comments", "default": true}
    },
    "required": ["project_key", "repository", "pr_id"]
  }
}
```

#### `post_pr_comments`
```json
{
  "name": "post_pr_comments",
  "description": "Post review comments to pull request",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_key": {"type": "string", "description": "Bitbucket project key"},
      "repository": {"type": "string", "description": "Repository name"},
      "pr_id": {"type": "string", "description": "Pull request ID"},
      "comments": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "text": {"type": "string", "description": "Comment text"},
            "file_path": {"type": "string", "description": "File path for inline comments"},
            "line": {"type": "number", "description": "Line number for inline comments"},
            "comment_type": {"type": "string", "enum": ["GENERAL", "INLINE"], "default": "GENERAL"}
          },
          "required": ["text"]
        }
      }
    },
    "required": ["project_key", "repository", "pr_id", "comments"]
  }
}
```

## Bitbucket Server REST API Integration

### Authentication
- **Method**: Personal Access Token (HTTP Bearer Authentication)
- **Configuration**: Token stored securely in MCP server configuration
- **Permissions Required**: Repository read/write, Pull request read/write/comment

### API Endpoints

#### Branch Operations
```
# Get all branches
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/branches

# Create branch
POST /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/branches
Body: {"name": "branch-name", "startPoint": "refs/heads/main"}

# Delete branch  
DELETE /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/branches/{BRANCH_NAME}

# Get tags
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/tags

# Get latest tag
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/tags?orderBy=MODIFICATION&limit=1
```

#### Search Operations
```
# Search code across project
GET /rest/api/1.0/projects/{PROJECT_KEY}/search/code?query={QUERY}&limit={LIMIT}

# Search in specific repository
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/search/code?query={QUERY}
```

#### Pull Request Operations
```
# Create pull request
POST /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/pull-requests
Body: {
  "title": "PR Title",
  "description": "PR Description", 
  "fromRef": {"id": "refs/heads/feature-branch"},
  "toRef": {"id": "refs/heads/main"},
  "reviewers": [{"user": {"name": "username"}}]
}

# List pull requests
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/pull-requests?state={STATE}&limit={LIMIT}

# Get pull request details
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/pull-requests/{PR_ID}

# Get pull request diff
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/pull-requests/{PR_ID}/diff

# Get pull request comments
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/pull-requests/{PR_ID}/comments

# Add pull request comment
POST /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/pull-requests/{PR_ID}/comments
Body: {"text": "Comment text"}

# Add inline comment
POST /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/pull-requests/{PR_ID}/comments
Body: {
  "text": "Inline comment",
  "anchor": {
    "diffType": "EFFECTIVE",
    "fromHash": "commit-hash",
    "toHash": "commit-hash", 
    "path": "file/path",
    "line": 42,
    "lineType": "ADDED"
  }
}
```

#### Repository Discovery Operations
```
# List all repositories in project with metadata
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos?limit={LIMIT}

# Get repository information
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}

# Get commits
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/commits

# Get file content
GET /rest/api/1.0/projects/{PROJECT_KEY}/repos/{REPOSITORY}/raw/{FILE_PATH}
```

## Technical Architecture

### Core Components
1. **MCP Server Framework**: Handles MCP protocol communication with AI assistants
2. **Bitbucket API Client**: Manages all REST API interactions with Bitbucket Server
3. **Git Operations Engine**: Performs local git operations and validations
4. **Security Scanner**: Basic security vulnerability detection for pre-commit checks
5. **Intelligence Layer**: Generates commit messages and PR descriptions

### Repository Discovery Workflow

The MCP server implements a clean two-step workflow for repository operations:

#### Step 1: Repository Discovery
- AI assistants use the `list_repositories` tool to retrieve all repositories in a project
- The tool returns repository names, descriptions, and metadata
- AI assistants can intelligently match user intentions with specific repositories from the list
- No complex server-side matching algorithms required

#### Step 2: Repository Operations  
- Once the correct repository is identified, AI assistants use the exact repository name
- All subsequent tools require exact repository names for reliability and performance
- Clear separation of concerns: discovery vs. operations
- Leverages AI assistants' natural language processing capabilities for intelligent matching

#### Benefits of This Approach
- **Simplicity**: Clean separation between discovery and operations
- **Reliability**: Exact names eliminate ambiguity in operations  
- **Performance**: No complex fuzzy matching overhead during operations
- **AI-Powered**: Leverages AI assistants' superior context understanding for repository selection
- **Maintainability**: Simpler codebase with fewer edge cases

### Security Considerations
- Personal Access Token stored securely with proper encryption
- API rate limiting implementation to prevent abuse
- Input validation for all user-provided parameters
- Audit logging for all operations performed

### Error Handling Strategy
- Comprehensive error handling for all API interactions
- Meaningful error messages returned to AI assistants
- Retry mechanisms for transient failures
- Fallback strategies for optional operations

## Success Metrics

### Primary Metrics
- Reduction in time spent on routine Git operations (target: 40% reduction)
- Improved code review quality through AI assistance
- Increased developer satisfaction with workflow automation

### Secondary Metrics
- Number of security issues caught before commit
- Consistency improvement in branch naming and PR descriptions
- Reduced manual errors in Git operations
- Improved workflow efficiency through streamlined repository discovery

## Risk Assessment and Mitigation

### Technical Risks
- **API Rate Limiting**: Implement intelligent request batching and caching
- **Network Connectivity**: Implement robust retry mechanisms and offline fallbacks
- **Token Expiration**: Automated token refresh and expiration monitoring

### Operational Risks
- **User Adoption**: Comprehensive documentation and training materials
- **Integration Issues**: Extensive testing with existing development workflows
- **Performance Impact**: Load testing and optimization for concurrent operations

## Conclusion

This Bitbucket MCP Server will significantly enhance developer productivity by automating routine Git operations and providing AI-assisted code review capabilities. The clean two-step repository discovery workflow leverages AI assistants' natural language processing capabilities while maintaining simplicity and reliability in the underlying implementation.

The integration with MCP-compatible AI assistants leverages existing AI capabilities for codebase exploration and intelligent code review, resulting in a more efficient and maintainable solution compared to building complex analysis engines from scratch.
