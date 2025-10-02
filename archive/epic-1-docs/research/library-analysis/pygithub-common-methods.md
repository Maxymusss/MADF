# PyGithub - Commonly Used Methods

**Library**: PyGithub
**Type**: Direct Python Library
**Purpose**: GitHub REST API v3 wrapper
**Documentation**: https://pygithub.readthedocs.io/

---

## Installation & Authentication

```python
from github import Github, Auth

# Authentication
auth = Auth.Token("your_token_here")
g = Github(auth=auth)
```

---

## Core Classes & Common Methods

### 1. Github (Main Class)

**Purpose**: Entry point for API access

**Common Methods** (5):
1. `get_repo(full_name_or_id)` - Get specific repository
2. `get_user(login=None)` - Get user (authenticated user if no login)
3. `get_organization(login)` - Get organization
4. `search_repositories(query)` - Search repos with query
5. `get_repos()` - List authenticated user's repositories

**Usage Priority**: HIGH - Required for all operations

**Example**:
```python
repo = g.get_repo("owner/repo_name")
user = g.get_user()
org = g.get_organization("org_name")
```

---

### 2. Repository Class

**Purpose**: Repository operations

**Common Methods** (15):
1. `get_contents(path)` - Retrieve file/directory contents
2. `get_branches()` - List all branches
3. `get_issues(state='open')` - List issues
4. `get_pulls(state='open')` - List pull requests
5. `create_issue(title, body)` - Create new issue
6. `create_pull(title, body, head, base)` - Create PR
7. `get_commits()` - List commits
8. `get_file_contents(path)` - Get file contents
9. `create_file(path, message, content)` - Create file with commit
10. `update_file(path, message, content, sha)` - Update file
11. `delete_file(path, message, sha)` - Delete file
12. `get_collaborators()` - List collaborators
13. `get_labels()` - List labels
14. `get_milestones()` - List milestones
15. `edit(name, description, homepage, private)` - Update repo settings

**Usage Priority**: HIGH - Core repository operations

**Example**:
```python
# File operations
contents = repo.get_contents("README.md")
repo.create_file("new_file.py", "Initial commit", "print('hello')")

# Issue/PR operations
issues = repo.get_issues(state='all')
pr = repo.create_pull(title="Feature", body="Description", head="feature-branch", base="main")
```

---

### 3. PullRequest Class

**Purpose**: Pull request management

**Common Methods** (10):
1. `get_comments()` - List PR comments
2. `get_commits()` - List PR commits
3. `get_files()` - List changed files
4. `create_comment(body)` - Add comment
5. `edit(title, body, state)` - Update PR
6. `merge(commit_message)` - Merge PR
7. `add_to_assignees(*assignees)` - Assign users
8. `add_to_labels(*labels)` - Add labels
9. `get_reviews()` - List reviews
10. `create_review(body, event)` - Create review (APPROVE/REQUEST_CHANGES/COMMENT)

**Usage Priority**: HIGH - PR workflow

**Example**:
```python
pr = repo.get_pull(123)
pr.create_comment("LGTM!")
pr.add_to_labels("ready-to-merge")
pr.merge(commit_message="Merge feature")
```

---

### 4. Issue Class

**Purpose**: Issue tracking

**Common Methods** (8):
1. `get_comments()` - List issue comments
2. `get_labels()` - List issue labels
3. `create_comment(body)` - Add comment
4. `edit(title, body, state)` - Update issue
5. `add_to_labels(*labels)` - Add labels
6. `add_to_assignees(*assignees)` - Assign users
7. `lock(lock_reason)` - Lock issue
8. `unlock()` - Unlock issue

**Usage Priority**: MEDIUM - Issue management

**Example**:
```python
issue = repo.get_issue(456)
issue.create_comment("Working on this")
issue.add_to_labels("bug", "high-priority")
issue.edit(state="closed")
```

---

### 5. Commit Class

**Purpose**: Commit operations

**Common Methods** (5):
1. `get_comments()` - List commit comments
2. `create_comment(body, line, path, position)` - Add commit comment
3. `get_check_runs()` - Get CI check runs
4. `get_statuses()` - Get commit statuses
5. `stats` - Commit statistics (additions, deletions)

**Usage Priority**: LOW - Mostly read-only inspection

**Example**:
```python
commit = repo.get_commit("abc123")
statuses = commit.get_statuses()
commit.create_comment("Found issue here")
```

---

### 6. User Class

**Purpose**: User information

**Common Methods** (5):
1. `get_repos()` - List user's repositories
2. `get_repo(name)` - Get user's specific repo
3. `get_gists()` - List user's gists
4. `get_followers()` - List followers
5. `get_following()` - List following

**Usage Priority**: MEDIUM - User operations

**Example**:
```python
user = g.get_user("username")
repos = user.get_repos()
```

---

### 7. Organization Class

**Purpose**: Organization management

**Common Methods** (6):
1. `get_repos()` - List org repositories
2. `create_repo(name, description, private)` - Create repo in org
3. `get_members()` - List org members
4. `get_teams()` - List org teams
5. `get_projects()` - List org projects
6. `get_issues()` - List org issues

**Usage Priority**: MEDIUM - Organization operations

**Example**:
```python
org = g.get_organization("org_name")
repos = org.get_repos()
org.create_repo("new_repo", private=True)
```

---

## MADF Implementation

**File**: [src/integrations/github_client.py](../../src/integrations/github_client.py)

**Implemented Methods** (18):
1. `search_repos(query, sort, order)` - Search repositories
2. `get_repo(full_name)` - Get repository
3. `list_repos(username, org)` - List user/org repos
4. `get_repo_contents(repo_name, path)` - Get contents
5. `get_pr(repo_name, pr_number)` - Get pull request
6. `list_prs(repo_name, state)` - List pull requests
7. `create_pr(repo_name, title, body, head, base)` - Create PR
8. `update_pr(repo_name, pr_number, title, body)` - Update PR
9. `merge_pr(repo_name, pr_number, commit_message)` - Merge PR
10. `get_issue(repo_name, issue_number)` - Get issue
11. `list_issues(repo_name, state)` - List issues
12. `create_issue(repo_name, title, body)` - Create issue
13. `update_issue(repo_name, issue_number, title, body)` - Update issue
14. `add_issue_comment(repo_name, issue_number, comment)` - Add comment
15. `get_file_contents(repo_name, file_path)` - Get file
16. `create_or_update_file(repo_name, file_path, content, message)` - File ops
17. `list_commits(repo_name, sha, path)` - List commits
18. `get_commit(repo_name, sha)` - Get commit

---

## Tool Count Summary

**Total PyGithub Methods**: 50+ across all classes
**Commonly Used**: 20-25 methods (80% of use cases)
**MADF Implementation**: 18 methods (core operations)

**Priority Breakdown**:
- **HIGH (15 methods)**: Repository, PullRequest, Github class operations
- **MEDIUM (8 methods)**: Issue, User, Organization operations
- **LOW (5 methods)**: Commit, Branch, Label operations

---

## Performance Characteristics

- **Speed**: Medium (GitHub API rate limits apply)
- **Rate Limits**: 5000 requests/hour (authenticated), 60/hour (unauthenticated)
- **Caching**: No built-in caching (implement client-side if needed)
- **Pagination**: Automatic via PaginatedList
- **Type Safety**: Full type hints in PyGithub 2.0+

---

## Testing Priority

**HIGH Priority** (must test):
1. `get_repo()` - Core repository access
2. `get_contents()` - File reading
3. `create_pull()`, `merge_pr()` - PR workflow
4. `list_issues()`, `create_issue()` - Issue tracking
5. `search_repositories()` - Repository discovery

**MEDIUM Priority**:
1. `create_file()`, `update_file()` - File management
2. `get_commits()` - History inspection
3. Organization/User operations

**LOW Priority**:
1. Commit comments
2. Advanced review operations
3. Label/milestone management

---

## Comparison: PyGithub vs gh CLI vs git CLI

| Operation | PyGithub | gh CLI | git CLI | Winner |
|-----------|----------|--------|---------|--------|
| Create PR | ✓ Programmatic | ✓ Interactive | ✗ | Tie |
| List PRs | ✓ Python objects | ✓ JSON output | ✗ | gh (scripting) |
| Merge PR | ✓ | ✓ | ✗ | Tie |
| Clone repo | ✗ | ✓ | ✓ | git (fastest) |
| Commit | ✗ | ✗ | ✓ | git (only option) |
| API calls | ✓ Full SDK | ✓ Simple | ✗ | PyGithub (type safety) |
| Bulk ops | ✓ Good | ✓ Best | ✗ | gh (JSON + jq) |

**PyGithub Strengths**:
- Best for Python codebases
- Type safety and IDE autocomplete
- Complex programmatic logic
- Full API coverage

**When to Use PyGithub**:
- LangGraph agent integration
- Python-based automation
- Complex workflows requiring state management
- Need type safety and error handling
