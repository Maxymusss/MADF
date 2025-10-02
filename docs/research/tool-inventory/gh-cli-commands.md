# GitHub CLI (gh) Commands

**Execution**: Via Claude Code `Bash` tool
**Category**: GitHub API and workflow commands
**Total Commands**: 50+ commands across 15+ categories

## Core Commands

### gh auth
- **Purpose**: Authenticate gh and git with GitHub
- **Commands**:
  - `gh auth login [options]`: Authenticate
  - `gh auth logout`: Remove authentication
  - `gh auth status`: View auth status
  - `gh auth refresh [options]`: Refresh credentials
  - `gh auth setup-git`: Configure git to use gh
- **Options** (login):
  - `--with-token`: Use token from stdin
  - `--hostname <string>`: GitHub hostname (for Enterprise)
  - `--web`: Authenticate via web browser
- **Use Cases**: Initial setup, token management
- **Returns**: Auth status, success/failure

### gh repo
- **Purpose**: Manage repositories
- **Commands**:
  - `gh repo create [name] [options]`: Create repository
  - `gh repo clone <repo>`: Clone repository
  - `gh repo list [owner] [options]`: List repositories
  - `gh repo view [repo] [options]`: View repository
  - `gh repo delete [repo]`: Delete repository
  - `gh repo fork [repo] [options]`: Fork repository
  - `gh repo rename <new-name>`: Rename repository
  - `gh repo archive [repo]`: Archive repository
  - `gh repo sync [repo]`: Sync fork
  - `gh repo edit [repo] [options]`: Edit repository settings
- **Options** (create):
  - `--public/--private/--internal`: Visibility
  - `--description <string>`: Description
  - `--homepage <url>`: Homepage URL
  - `--template <repo>`: Use template
- **Options** (list):
  - `--limit <int>`: Max repos to list
  - `--json <fields>`: JSON output
  - `--source`: Show source repos only (not forks)
  - `--fork`: Show forks only
- **Use Cases**: Repository management, bulk operations
- **Returns**: Repository info, operation status

### gh pr
- **Purpose**: Manage pull requests
- **Commands**:
  - `gh pr create [options]`: Create pull request
  - `gh pr list [options]`: List pull requests
  - `gh pr view [number] [options]`: View pull request
  - `gh pr checkout <number>`: Check out PR branch
  - `gh pr diff [number]`: View PR diff
  - `gh pr merge [number] [options]`: Merge pull request
  - `gh pr close [number]`: Close pull request
  - `gh pr reopen [number]`: Reopen pull request
  - `gh pr ready [number]`: Mark draft as ready
  - `gh pr review [number] [options]`: Review pull request
  - `gh pr status`: Show status of PRs
  - `gh pr comment [number] [options]`: Comment on PR
  - `gh pr edit [number] [options]`: Edit pull request
- **Options** (create):
  - `--title <string>`: PR title
  - `--body <string>`: PR body
  - `--base <branch>`: Base branch
  - `--head <branch>`: Head branch
  - `--draft`: Create as draft
  - `--assignee <users>`: Assign users
  - `--reviewer <users>`: Request reviews
  - `--label <labels>`: Add labels
- **Options** (list):
  - `--state <state>`: all/open/closed/merged
  - `--author <user>`: Filter by author
  - `--assignee <user>`: Filter by assignee
  - `--label <labels>`: Filter by labels
  - `--limit <int>`: Max PRs to list
  - `--json <fields>`: JSON output
- **Options** (merge):
  - `--merge/--squash/--rebase`: Merge strategy
  - `--auto`: Auto-merge when checks pass
  - `--delete-branch`: Delete branch after merge
- **Use Cases**: PR workflow, code review, bulk PR operations
- **Returns**: PR details, operation status, JSON data

### gh issue
- **Purpose**: Manage issues
- **Commands**:
  - `gh issue create [options]`: Create issue
  - `gh issue list [options]`: List issues
  - `gh issue view [number] [options]`: View issue
  - `gh issue close [number]`: Close issue
  - `gh issue reopen [number]`: Reopen issue
  - `gh issue status`: Show issue status
  - `gh issue comment [number] [options]`: Comment on issue
  - `gh issue edit [number] [options]`: Edit issue
  - `gh issue delete [number]`: Delete issue
  - `gh issue pin [number]`: Pin issue
  - `gh issue unpin [number]`: Unpin issue
- **Options** (create):
  - `--title <string>`: Issue title
  - `--body <string>`: Issue body
  - `--assignee <users>`: Assign users
  - `--label <labels>`: Add labels
  - `--milestone <name>`: Set milestone
  - `--project <name>`: Add to project
- **Options** (list):
  - `--state <state>`: all/open/closed
  - `--author <user>`: Filter by author
  - `--assignee <user>`: Filter by assignee
  - `--label <labels>`: Filter by labels
  - `--limit <int>`: Max issues to list
  - `--json <fields>`: JSON output
- **Use Cases**: Issue tracking, project management
- **Returns**: Issue details, operation status

### gh release
- **Purpose**: Manage releases
- **Commands**:
  - `gh release create <tag> [files...] [options]`: Create release
  - `gh release list [options]`: List releases
  - `gh release view <tag> [options]`: View release
  - `gh release delete <tag>`: Delete release
  - `gh release download [tag] [options]`: Download assets
  - `gh release upload <tag> <files...>`: Upload assets
  - `gh release edit <tag> [options]`: Edit release
- **Options** (create):
  - `--title <string>`: Release title
  - `--notes <string>`: Release notes
  - `--notes-file <file>`: Read notes from file
  - `--draft`: Create as draft
  - `--prerelease`: Mark as prerelease
  - `--target <branch>`: Target branch/commit
- **Use Cases**: Version releases, asset distribution
- **Returns**: Release details, download progress

### gh gist
- **Purpose**: Manage gists
- **Commands**:
  - `gh gist create [files...] [options]`: Create gist
  - `gh gist list [options]`: List gists
  - `gh gist view <id> [options]`: View gist
  - `gh gist delete <id>`: Delete gist
  - `gh gist edit <id> <file>`: Edit gist
  - `gh gist clone <id>`: Clone gist
- **Options** (create):
  - `--public/--secret`: Visibility
  - `--desc <string>`: Description
  - `--filename <string>`: Filename
- **Use Cases**: Share code snippets, quick file sharing
- **Returns**: Gist URL, content

### gh browse
- **Purpose**: Open repository/PR/issue in browser
- **Usage**: `gh browse [options] [number]`
- **Options**:
  - `--branch <branch>`: Open branch
  - `--commit <sha>`: Open commit
  - `--projects`: Open projects
  - `--settings`: Open settings
  - `--wiki`: Open wiki
- **Use Cases**: Quick navigation to web UI
- **Returns**: Opens browser, prints URL

### gh org
- **Purpose**: Manage organizations
- **Commands**:
  - `gh org list`: List organizations
  - `gh org view <org> [options]`: View organization
- **Use Cases**: Organization management
- **Returns**: Organization details

### gh project
- **Purpose**: Work with GitHub Projects
- **Commands**:
  - `gh project list [options]`: List projects
  - `gh project view <number> [options]`: View project
  - `gh project create [options]`: Create project
  - `gh project close <number>`: Close project
  - `gh project reopen <number>`: Reopen project
  - `gh project delete <number>`: Delete project
  - `gh project edit <number> [options]`: Edit project
  - `gh project item-add <number> [options]`: Add item
  - `gh project item-list <number> [options]`: List items
- **Use Cases**: Project board management
- **Returns**: Project details, item lists

### gh codespace
- **Purpose**: Connect to and manage codespaces
- **Commands**:
  - `gh codespace create [options]`: Create codespace
  - `gh codespace list [options]`: List codespaces
  - `gh codespace ssh [options]`: SSH into codespace
  - `gh codespace delete [options]`: Delete codespace
  - `gh codespace stop [options]`: Stop codespace
  - `gh codespace code [options]`: Open in VS Code
  - `gh codespace logs`: View logs
- **Use Cases**: Remote development environments
- **Returns**: Codespace details, SSH connection

## GitHub Actions Commands

### gh run
- **Purpose**: View details about workflow runs
- **Commands**:
  - `gh run list [options]`: List workflow runs
  - `gh run view [run-id] [options]`: View run details
  - `gh run watch <run-id>`: Watch run in real-time
  - `gh run rerun [run-id] [options]`: Rerun workflow
  - `gh run cancel [run-id]`: Cancel run
  - `gh run delete [run-id]`: Delete run
  - `gh run download [run-id] [options]`: Download artifacts
- **Options** (list):
  - `--workflow <name>`: Filter by workflow
  - `--status <status>`: Filter by status (completed/failure/success)
  - `--branch <branch>`: Filter by branch
  - `--limit <int>`: Max runs to list
  - `--json <fields>`: JSON output
- **Use Cases**: CI/CD monitoring, debugging workflows
- **Returns**: Run details, logs, artifacts

### gh workflow
- **Purpose**: View details about GitHub Actions workflows
- **Commands**:
  - `gh workflow list [options]`: List workflows
  - `gh workflow view <workflow> [options]`: View workflow
  - `gh workflow run <workflow> [options]`: Trigger workflow
  - `gh workflow enable <workflow>`: Enable workflow
  - `gh workflow disable <workflow>`: Disable workflow
- **Options** (run):
  - `--ref <branch>`: Branch/tag to run on
  - `--raw-field <key>=<value>`: Set input value
- **Use Cases**: Workflow management, manual triggers
- **Returns**: Workflow details, run ID

### gh cache
- **Purpose**: Manage GitHub Actions caches
- **Commands**:
  - `gh cache list [options]`: List caches
  - `gh cache delete [cache-id]`: Delete cache
- **Use Cases**: Cache management, cleanup
- **Returns**: Cache list, deletion status

## Additional Commands

### gh api
- **Purpose**: Make authenticated GitHub API request
- **Usage**: `gh api <endpoint> [options]`
- **Options**:
  - `-X, --method <method>`: HTTP method (GET/POST/PUT/DELETE)
  - `-F, --field <key>=<value>`: Add parameter
  - `-H, --header <header>`: Add header
  - `--paginate`: Paginate results
  - `--jq <expression>`: Filter with jq
- **Examples**:
  - `gh api repos/{owner}/{repo}/pulls`
  - `gh api -X POST repos/{owner}/{repo}/issues -f title="Bug"`
  - `gh api --paginate repos/{owner}/{repo}/issues --jq '.[].title'`
- **Use Cases**: Custom API operations, bulk operations, automation
- **Returns**: Raw JSON API response

### gh search
- **Purpose**: Search for repositories/issues/pull requests
- **Commands**:
  - `gh search repos <query> [options]`: Search repositories
  - `gh search issues <query> [options]`: Search issues
  - `gh search prs <query> [options]`: Search pull requests
  - `gh search code <query> [options]`: Search code
- **Options**:
  - `--limit <int>`: Max results
  - `--owner <user>`: Filter by owner
  - `--language <lang>`: Filter by language
  - `--stars <range>`: Filter by stars (e.g., ">1000")
  - `--created <date>`: Filter by creation date
  - `--json <fields>`: JSON output
- **Use Cases**: Find repositories, research, bulk analysis
- **Returns**: Search results (repos/issues/PRs/code)

### gh secret
- **Purpose**: Manage GitHub secrets
- **Commands**:
  - `gh secret list [options]`: List secrets
  - `gh secret set <name> [options]`: Set secret
  - `gh secret remove <name>`: Remove secret
- **Options** (set):
  - `--body <string>`: Secret value
  - `--org <org>`: Organization secret
  - `--repo <repo>`: Repository secret
  - `--env <env>`: Environment secret
- **Use Cases**: Manage Actions secrets, CI/CD configuration
- **Returns**: Secret list, operation status

### gh variable
- **Purpose**: Manage GitHub Actions variables
- **Commands**:
  - `gh variable list [options]`: List variables
  - `gh variable set <name> [options]`: Set variable
  - `gh variable remove <name>`: Remove variable
- **Options**: Similar to gh secret
- **Use Cases**: Manage Actions variables, configuration
- **Returns**: Variable list, operation status

### gh label
- **Purpose**: Manage labels
- **Commands**:
  - `gh label list [options]`: List labels
  - `gh label create <name> [options]`: Create label
  - `gh label delete <name>`: Delete label
  - `gh label edit <name> [options]`: Edit label
  - `gh label clone <repo>`: Clone labels from another repo
- **Options** (create):
  - `--color <color>`: Label color
  - `--description <string>`: Description
- **Use Cases**: Issue/PR organization, project setup
- **Returns**: Label list, operation status

### gh gpg-key
- **Purpose**: Manage GPG keys
- **Commands**:
  - `gh gpg-key list`: List GPG keys
  - `gh gpg-key add [key-file]`: Add GPG key
  - `gh gpg-key delete <key-id>`: Delete GPG key
- **Use Cases**: Commit signing, security
- **Returns**: GPG key list, operation status

### gh ssh-key
- **Purpose**: Manage SSH keys
- **Commands**:
  - `gh ssh-key list`: List SSH keys
  - `gh ssh-key add [key-file]`: Add SSH key
  - `gh ssh-key delete <key-id>`: Delete SSH key
- **Use Cases**: Authentication, security
- **Returns**: SSH key list, operation status

### gh alias
- **Purpose**: Create command shortcuts
- **Commands**:
  - `gh alias list`: List aliases
  - `gh alias set <alias> <expansion>`: Create alias
  - `gh alias delete <alias>`: Delete alias
- **Examples**:
  - `gh alias set pv 'pr view'`
  - `gh alias set bugs 'issue list --label=bug'`
- **Use Cases**: Custom workflows, frequently used commands
- **Returns**: Alias list, operation status

### gh extension
- **Purpose**: Manage gh extensions
- **Commands**:
  - `gh extension list`: List installed extensions
  - `gh extension install <repo>`: Install extension
  - `gh extension remove <name>`: Remove extension
  - `gh extension upgrade <name>`: Upgrade extension
  - `gh extension create [name]`: Create extension
- **Use Cases**: Extend gh functionality
- **Returns**: Extension list, operation status

### gh ruleset
- **Purpose**: View info about repository rulesets
- **Commands**:
  - `gh ruleset list [options]`: List rulesets
  - `gh ruleset view <ruleset-id>`: View ruleset
- **Use Cases**: Repository protection rules, compliance
- **Returns**: Ruleset details

### gh attestation
- **Purpose**: Work with artifact attestations
- **Commands**:
  - `gh attestation verify <artifact> [options]`: Verify attestation
- **Use Cases**: Supply chain security, artifact verification
- **Returns**: Verification status

### gh config
- **Purpose**: Manage configuration for gh
- **Commands**:
  - `gh config list`: List config
  - `gh config get <key>`: Get config value
  - `gh config set <key> <value>`: Set config value
- **Use Cases**: gh configuration, defaults
- **Returns**: Config values

### gh completion
- **Purpose**: Generate shell completion scripts
- **Usage**: `gh completion -s <shell>`
- **Shells**: bash, zsh, fish, powershell
- **Use Cases**: Shell autocomplete
- **Returns**: Completion script

### gh status
- **Purpose**: Print information about relevant issues/PRs/notifications
- **Usage**: `gh status [options]`
- **Options**:
  - `--org <org>`: Filter by organization
- **Use Cases**: Dashboard view, quick status check
- **Returns**: Summary of assigned issues, PRs, reviews

## Alias Commands

### gh co
- **Purpose**: Alias for "pr checkout"
- **Usage**: `gh co <number>`
- **Use Cases**: Quick PR checkout
- **Returns**: Checkout confirmation

## JSON Output & Scripting

### JSON Fields
Most list/view commands support `--json <fields>` for structured output:

**Pull Requests**:
- `gh pr list --json number,title,state,author,createdAt,updatedAt,url`
- Fields: number, title, body, state, author, assignees, labels, reviewers, url, createdAt, updatedAt, closedAt, mergedAt

**Issues**:
- `gh issue list --json number,title,state,author,createdAt,labels`
- Fields: number, title, body, state, author, assignees, labels, url, createdAt, updatedAt, closedAt

**Repositories**:
- `gh repo list --json name,description,visibility,createdAt,pushedAt`
- Fields: name, nameWithOwner, description, visibility, isPrivate, isFork, url, createdAt, updatedAt, pushedAt

**Workflow Runs**:
- `gh run list --json databaseId,status,conclusion,name,headBranch`
- Fields: databaseId, status, conclusion, name, displayTitle, headBranch, createdAt, updatedAt, url

### jq Integration
Use `--jq` for filtering:
```bash
gh pr list --json number,title --jq '.[] | select(.title | contains("bug"))'
gh repo list --json name,stargazerCount --jq 'sort_by(.stargazerCount) | reverse | .[0:5]'
```

## Performance Characteristics

| Command | Speed | Output Size | Use Case Priority |
|---------|-------|-------------|-------------------|
| gh pr list | Medium | Small-Large | High - PR workflow |
| gh pr view | Fast | Small-Medium | High - review |
| gh pr create | Medium | Small | High - workflow |
| gh pr merge | Medium | Small | High - workflow |
| gh issue list | Medium | Small-Large | High - tracking |
| gh repo list | Medium | Small-Large | Medium - discovery |
| gh api | Medium | Variable | High - automation |
| gh run list | Medium | Small-Large | High - CI/CD |
| gh workflow run | Fast | Small | Medium - triggers |
| gh search | Slow | Medium-Large | Low - research |
| gh release create | Medium | Small | Medium - publishing |
| gh gist create | Fast | Small | Low - sharing |
| gh browse | Very Fast | None | Medium - navigation |

## Tool Comparison: gh CLI vs PyGithub vs git CLI

### Use Case Matrix

| Operation | gh CLI | PyGithub | git CLI | Best Choice |
|-----------|--------|----------|---------|-------------|
| Create PR | ✓ Interactive | ✓ Programmatic | ✗ | gh (interactive), PyGithub (automated) |
| List PRs | ✓ JSON output | ✓ Python objects | ✗ | Tie - gh for JSON, PyGithub for Python |
| Merge PR | ✓ | ✓ | ✗ | Tie - both good |
| Search repos | ✓ | ✓ | ✗ | gh (JSON output for scripts) |
| Bulk operations | ✓ Best | ✓ Good | ✗ | gh (JSON + jq pipeline) |
| CI status | ✓ Best | ✓ Limited | ✗ | gh (native Actions support) |
| Clone repo | ✓ | ✗ | ✓ Best | git (native, fastest) |
| Commit changes | ✗ | ✗ | ✓ Best | git (only option) |
| Push changes | ✗ | ✗ | ✓ Best | git (only option) |
| API calls | ✓ Simple | ✓ Full SDK | ✗ | PyGithub (type safety), gh (quick scripts) |
| Interactive workflow | ✓ Best | ✗ | ✗ | gh (prompts, confirmation) |
| Python integration | ✗ | ✓ Best | ✗ | PyGithub (native Python) |

### Strengths

**gh CLI**:
- Best for interactive workflows (prompts, confirmations)
- Best for bulk operations (JSON output + jq)
- Best for GitHub Actions integration
- Best for quick one-liners
- Native browser integration (`gh browse`)

**PyGithub**:
- Best for Python codebases
- Best for type safety and IDE autocomplete
- Best for complex programmatic logic
- Best for full API coverage

**git CLI**:
- Best (only option) for local repository operations
- Best for commits, branches, merges
- Best for performance on local operations

## Claude Code Integration Notes

### Execution Method
All gh commands executed via `Bash` tool:
```javascript
Bash({
  command: "gh pr list --state all --limit 100 --json number,title,state",
  description: "List all pull requests with JSON output"
})
```

### Authentication
- Requires `gh auth login` before first use
- Token can be provided via `gh auth login --with-token < token.txt`
- Check auth status: `gh auth status`

### Performance Tips
- Use `--json` for structured output (faster parsing)
- Use `--jq` for filtering (reduce output size)
- Use `--limit` to control result count
- Use `--paginate` for complete datasets (slower)
- Batch related operations when possible

### Common Workflows

**List all open PRs with details**:
```bash
gh pr list --state open --json number,title,author,createdAt
```

**Create PR with all metadata**:
```bash
gh pr create --title "feat: new feature" --body "Description" --assignee @me --label enhancement
```

**Bulk search and filter**:
```bash
gh api --paginate repos/{owner}/{repo}/issues --jq '.[] | select(.labels[].name == "bug") | {number, title}'
```

**Monitor CI runs**:
```bash
gh run list --workflow CI --limit 10 --json status,conclusion,createdAt
```

**Search repos and clone top result**:
```bash
gh search repos "topic:python stars:>1000" --limit 1 --json fullName --jq '.[0].fullName' | xargs gh repo clone
```

## Total Command Count

- **Core Commands**: 10 (auth, repo, pr, issue, release, gist, browse, org, project, codespace)
- **Actions Commands**: 3 (run, workflow, cache)
- **Additional Commands**: 12+ (api, search, secret, variable, label, gpg-key, ssh-key, alias, extension, ruleset, attestation, config, completion, status)
- **Total**: 50+ commands
- **Subcommands**: 200+ total operations across all commands

## Integration with PyGithub

When to use each:

**Use gh CLI when**:
- Need interactive prompts
- Need JSON output for scripting
- Working with GitHub Actions
- Need bulk operations with jq
- Need browser integration

**Use PyGithub when**:
- Building Python applications
- Need type safety and IDE support
- Need complex programmatic logic
- Need full API coverage
- Integrating with LangGraph agents

**Use both when**:
- gh for data gathering (JSON output)
- PyGithub for processing (Python objects)
- Example: `gh pr list --json | python script.py` where script uses PyGithub for updates
