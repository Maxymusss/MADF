# git CLI Commands

**Execution**: Via Claude Code `Bash` tool
**Category**: Version control system commands
**Total Commands**: 30+ common commands, 150+ total git commands

## Repository Setup

### git init
- **Purpose**: Create empty Git repository
- **Usage**: `git init [directory]`
- **Use Cases**: Start new project
- **Returns**: Initialized repository message

### git clone
- **Purpose**: Clone repository into new directory
- **Usage**: `git clone <url> [directory]`
- **Options**:
  - `--depth <n>`: Shallow clone (partial history)
  - `--branch <name>`: Clone specific branch
  - `--recursive`: Clone with submodules
- **Use Cases**: Get existing repository
- **Returns**: Cloning progress, success message

## Working Area Operations

### git add
- **Purpose**: Add file contents to staging index
- **Usage**: `git add <pathspec>...`
- **Options**:
  - `-A, --all`: Add all changes
  - `-p, --patch`: Interactive staging
  - `-u, --update`: Add modified files only
- **Use Cases**: Stage changes for commit
- **Returns**: Silent on success

### git mv
- **Purpose**: Move or rename file/directory/symlink
- **Usage**: `git mv <source> <destination>`
- **Use Cases**: Rename files with git tracking
- **Returns**: Silent on success

### git restore
- **Purpose**: Restore working tree files
- **Usage**: `git restore [options] <pathspec>...`
- **Options**:
  - `--staged`: Unstage files
  - `--source <tree>`: Restore from specific commit
- **Use Cases**: Discard local changes, unstage files
- **Returns**: Silent on success

### git rm
- **Purpose**: Remove files from working tree and index
- **Usage**: `git rm [options] <file>...`
- **Options**:
  - `-r`: Recursive (for directories)
  - `--cached`: Remove from index only
  - `-f, --force`: Force removal
- **Use Cases**: Delete files with git tracking
- **Returns**: File removal messages

## History & State Examination

### git status
- **Purpose**: Show working tree status
- **Usage**: `git status [options]`
- **Options**:
  - `-s, --short`: Short format
  - `-b, --branch`: Show branch info
  - `--porcelain`: Machine-readable format
- **Use Cases**: Check modified files, staged changes, branch status
- **Returns**: Detailed status of working tree

### git diff
- **Purpose**: Show changes between commits/tree/working tree
- **Usage**: `git diff [options] [<commit>] [--] [<path>...]`
- **Options**:
  - `--cached, --staged`: Show staged changes
  - `--name-only`: Show only file names
  - `--stat`: Show statistics
  - `<commit1>..<commit2>`: Diff between commits
- **Use Cases**: Review changes before commit, compare branches
- **Returns**: Unified diff format

### git log
- **Purpose**: Show commit logs
- **Usage**: `git log [options] [<revision range>] [[--] <path>...]`
- **Options**:
  - `--oneline`: Compact format
  - `--graph`: ASCII graph
  - `--stat`: Include file statistics
  - `--author=<pattern>`: Filter by author
  - `-n <number>`: Limit number of commits
  - `--since=<date>`: Filter by date
  - `--format=<format>`: Custom format
- **Use Cases**: Review history, find commits, generate changelogs
- **Returns**: Commit history with details

### git show
- **Purpose**: Show various types of objects
- **Usage**: `git show [options] <object>...`
- **Use Cases**: View commit details, file contents at commit
- **Returns**: Object details (commit, tree, blob, tag)

### git grep
- **Purpose**: Print lines matching pattern in repository
- **Usage**: `git grep [options] <pattern> [<path>...]`
- **Options**:
  - `-n, --line-number`: Show line numbers
  - `-i, --ignore-case`: Case insensitive
  - `-v, --invert-match`: Invert match
  - `-E, --extended-regexp`: Extended regex
- **Use Cases**: Search repository contents
- **Returns**: Matching lines with file paths

### git bisect
- **Purpose**: Binary search to find bug-introducing commit
- **Usage**:
  - `git bisect start`
  - `git bisect bad [<commit>]`
  - `git bisect good <commit>`
  - `git bisect reset`
- **Use Cases**: Find regression commit
- **Returns**: Bisect status, suspected commit

## Branch & Tag Management

### git branch
- **Purpose**: List, create, or delete branches
- **Usage**: `git branch [options] [<branch>]`
- **Options**:
  - `-a, --all`: List all branches (local + remote)
  - `-d, --delete <branch>`: Delete branch
  - `-D`: Force delete
  - `-m, --move <old> <new>`: Rename branch
  - `-r, --remotes`: List remote branches
  - `--merged`: List merged branches
- **Use Cases**: Branch management
- **Returns**: Branch list or operation result

### git switch
- **Purpose**: Switch branches (modern alternative to checkout)
- **Usage**: `git switch [options] <branch>`
- **Options**:
  - `-c, --create <branch>`: Create and switch
  - `-d, --detach`: Detached HEAD
- **Use Cases**: Change active branch
- **Returns**: Branch switch confirmation

### git checkout
- **Purpose**: Switch branches or restore files (legacy)
- **Usage**: `git checkout [options] <branch>`
- **Options**:
  - `-b <branch>`: Create and switch
  - `--track <remote>/<branch>`: Track remote branch
  - `-- <file>`: Restore file
- **Use Cases**: Branch switching, file restoration
- **Returns**: Branch switch or file restore confirmation

### git tag
- **Purpose**: Create, list, delete, verify tags
- **Usage**: `git tag [options] [<tagname>] [<commit>]`
- **Options**:
  - `-a, --annotate`: Annotated tag
  - `-m <message>`: Tag message
  - `-d, --delete <tag>`: Delete tag
  - `-l, --list`: List tags
- **Use Cases**: Version marking, releases
- **Returns**: Tag list or creation confirmation

## Commits & History Modification

### git commit
- **Purpose**: Record changes to repository
- **Usage**: `git commit [options]`
- **Options**:
  - `-m <message>`: Commit message
  - `-a, --all`: Auto-stage modified files
  - `--amend`: Amend previous commit
  - `--no-verify`: Skip hooks
  - `--author=<author>`: Override author
- **Use Cases**: Save changes to repository
- **Returns**: Commit hash, files changed, insertions/deletions

### git merge
- **Purpose**: Join development histories together
- **Usage**: `git merge [options] <commit>...`
- **Options**:
  - `--ff-only`: Fast-forward only
  - `--no-ff`: Create merge commit
  - `--squash`: Squash commits
  - `--abort`: Abort merge
- **Use Cases**: Integrate branches
- **Returns**: Merge result (fast-forward, merge commit, conflicts)

### git rebase
- **Purpose**: Reapply commits on top of another base
- **Usage**: `git rebase [options] [<upstream> [<branch>]]`
- **Options**:
  - `-i, --interactive`: Interactive rebase (NOT SUPPORTED in Claude Code - requires interactive input)
  - `--continue`: Continue after conflict resolution
  - `--abort`: Abort rebase
  - `--skip`: Skip current commit
- **Use Cases**: Linear history, cleanup commits
- **Returns**: Rebase progress, conflicts

### git reset
- **Purpose**: Reset current HEAD to specified state
- **Usage**: `git reset [options] [<commit>]`
- **Options**:
  - `--soft`: Keep changes staged
  - `--mixed` (default): Unstage changes
  - `--hard`: Discard all changes (DESTRUCTIVE)
- **Use Cases**: Undo commits, unstage files
- **Returns**: Reset confirmation

### git stash
- **Purpose**: Stash changes in dirty working directory
- **Usage**: `git stash [options]`
- **Commands**:
  - `git stash push [<pathspec>...]`: Stash changes
  - `git stash list`: List stashes
  - `git stash pop [<stash>]`: Apply and remove stash
  - `git stash apply [<stash>]`: Apply stash
  - `git stash drop [<stash>]`: Remove stash
  - `git stash clear`: Remove all stashes
- **Use Cases**: Temporarily save work, switch contexts
- **Returns**: Stash operation result

## Collaboration & Remote Operations

### git fetch
- **Purpose**: Download objects and refs from remote
- **Usage**: `git fetch [options] [<remote>]`
- **Options**:
  - `--all`: Fetch all remotes
  - `--prune`: Remove deleted remote branches
  - `--tags`: Fetch tags
- **Use Cases**: Update remote-tracking branches
- **Returns**: Fetch progress, branches updated

### git pull
- **Purpose**: Fetch and integrate with repository/branch
- **Usage**: `git pull [options] [<remote> [<branch>]]`
- **Options**:
  - `--rebase`: Rebase instead of merge
  - `--ff-only`: Fast-forward only
  - `--no-commit`: Don't auto-commit merge
- **Use Cases**: Update local branch with remote changes
- **Returns**: Fetch + merge/rebase result

### git push
- **Purpose**: Update remote refs and associated objects
- **Usage**: `git push [options] [<remote> [<refspec>...]]`
- **Options**:
  - `-u, --set-upstream`: Set upstream tracking
  - `--force`: Force update (DESTRUCTIVE - avoid on main/master)
  - `--force-with-lease`: Safer force push
  - `--delete <branch>`: Delete remote branch
  - `--tags`: Push tags
- **Use Cases**: Upload local commits to remote
- **Returns**: Push progress, branch updates

### git remote
- **Purpose**: Manage tracked repositories
- **Usage**: `git remote [options] [<command>]`
- **Commands**:
  - `git remote add <name> <url>`: Add remote
  - `git remote remove <name>`: Remove remote
  - `git remote -v`: List remotes with URLs
  - `git remote show <name>`: Show remote details
  - `git remote rename <old> <new>`: Rename remote
- **Use Cases**: Manage remote repositories
- **Returns**: Remote list or operation result

## Advanced Commands

### git cherry-pick
- **Purpose**: Apply changes from specific commits
- **Usage**: `git cherry-pick [options] <commit>...`
- **Options**:
  - `--continue`: Continue after conflict resolution
  - `--abort`: Abort cherry-pick
  - `-n, --no-commit`: Don't auto-commit
- **Use Cases**: Apply specific commits to current branch
- **Returns**: Cherry-pick result

### git revert
- **Purpose**: Revert existing commits
- **Usage**: `git revert [options] <commit>...`
- **Options**:
  - `-n, --no-commit`: Don't auto-commit
  - `--continue`: Continue after conflict resolution
  - `--abort`: Abort revert
- **Use Cases**: Undo commits by creating inverse commit
- **Returns**: Revert commit details

### git backfill
- **Purpose**: Download missing objects in partial clone
- **Usage**: `git backfill [options]`
- **Use Cases**: Complete partial clone history
- **Returns**: Download progress

### git config
- **Purpose**: Get and set repository/global options
- **Usage**: `git config [options] <name> [<value>]`
- **Options**:
  - `--global`: User-level config
  - `--local`: Repository-level config
  - `--list`: List all config
  - `--get <name>`: Get value
  - `--unset <name>`: Remove value
- **Use Cases**: Configure git behavior, user info
- **Returns**: Config value or operation result
- **Claude Code Safety**: NEVER update git config unless explicitly requested

### git clean
- **Purpose**: Remove untracked files
- **Usage**: `git clean [options]`
- **Options**:
  - `-n, --dry-run`: Preview what will be deleted
  - `-f, --force`: Actually delete
  - `-d`: Remove directories
  - `-x`: Remove ignored files too
- **Use Cases**: Clean working directory
- **Returns**: Files to be/that were removed
- **Claude Code Safety**: ALWAYS use -n first

## Inspection & Debugging

### git blame
- **Purpose**: Show what revision/author last modified each line
- **Usage**: `git blame [options] <file>`
- **Options**:
  - `-L <start>,<end>`: Limit to line range
  - `-w`: Ignore whitespace
- **Use Cases**: Find who changed code, when
- **Returns**: Line-by-line annotation with commits

### git reflog
- **Purpose**: Show reference logs (HEAD history)
- **Usage**: `git reflog [options]`
- **Use Cases**: Recover lost commits, undo mistakes
- **Returns**: HEAD movement history

### git describe
- **Purpose**: Give object human-readable name
- **Usage**: `git describe [options] [<commit-ish>]`
- **Options**:
  - `--tags`: Use any tag
  - `--abbrev=<n>`: Abbreviation length
- **Use Cases**: Generate version strings
- **Returns**: Tag-based description

## Submodule Management

### git submodule
- **Purpose**: Manage submodules
- **Usage**: `git submodule [options] <command>`
- **Commands**:
  - `git submodule add <url> <path>`: Add submodule
  - `git submodule init`: Initialize submodules
  - `git submodule update`: Update submodules
  - `git submodule status`: Show submodule status
- **Use Cases**: Manage nested repositories
- **Returns**: Submodule operation results

## Performance Characteristics

| Command | Speed | Output Size | Use Case Priority |
|---------|-------|-------------|-------------------|
| git status | Fast | Small-Medium | High - frequent use |
| git diff | Fast | Small-Large | High - review changes |
| git log | Fast | Medium-Large | High - history review |
| git add | Very Fast | None | High - staging |
| git commit | Fast | Small | High - save work |
| git push | Medium | Small | High - share work |
| git pull | Medium | Small-Medium | High - sync work |
| git fetch | Medium | Small | Medium - update refs |
| git branch | Very Fast | Small | Medium - management |
| git merge | Fast | Small-Medium | Medium - integration |
| git rebase | Medium | Medium | Medium - cleanup |
| git stash | Fast | Small | Medium - context switch |
| git grep | Very Fast | Medium | Medium - search |
| git show | Fast | Small-Medium | Low - inspection |
| git blame | Fast | Medium | Low - debugging |
| git reflog | Very Fast | Small | Low - recovery |

## Tool Comparison: git CLI vs PyGithub vs gh CLI

### Repository Operations
- **git CLI**: Best for commits, branches, merges, local operations
- **PyGithub**: Best for GitHub API operations (PRs, issues, releases)
- **gh CLI**: Best for interactive GitHub workflows, bulk operations

### Use Case Matrix

| Operation | Best Tool | Reason |
|-----------|-----------|--------|
| Clone repo | git clone | Native, fastest |
| Create commit | git commit | Native, local |
| Push changes | git push | Native, direct |
| Create PR | gh pr create | Interactive, rich features |
| Merge PR | gh pr merge | GitHub API, validation |
| List issues | PyGithub or gh | API access, filtering |
| Search repos | PyGithub or gh | API access, programmatic |
| Bulk operations | gh CLI | JSON output, scripting |
| View PR status | gh pr status | Quick overview |
| Check CI status | gh run list | Actions integration |

## Claude Code Integration Notes

### Execution Method
All git commands executed via `Bash` tool:
```javascript
Bash({
  command: "git status",
  description: "Check working tree status"
})
```

### Safety Constraints
- **NEVER** run `git config` without user approval
- **ALWAYS** preview destructive operations (`git clean -n`, `git reset --hard`)
- **AVOID** `git push --force` to main/master (warn user)
- **NEVER** use interactive flags (`-i`, `--interactive`) - not supported in Bash tool
- **NEVER** skip hooks (`--no-verify`) unless explicitly requested

### Performance Tips
- Batch related git commands: `git add . && git commit -m "message" && git push`
- Use `--oneline` for git log in scripts
- Use `--porcelain` for machine-readable output
- Use `--name-only` to reduce diff output

### Common Workflows

**Commit Changes**:
```bash
git add . && git commit -m "feat: add feature" && git push
```

**Create Branch and PR**:
```bash
git checkout -b feature-branch && git push -u origin feature-branch && gh pr create
```

**Review Changes Before Commit**:
```bash
git status && git diff --staged
```

**Undo Last Commit (keep changes)**:
```bash
git reset --soft HEAD~1
```

**Update from Remote**:
```bash
git fetch --prune && git pull --rebase
```

## Total Command Count

- **Core Commands**: ~30 commonly used
- **Total Commands**: 150+ (including porcelain and plumbing)
- **Claude Code Usage**: Execute via `Bash` tool with safety constraints
