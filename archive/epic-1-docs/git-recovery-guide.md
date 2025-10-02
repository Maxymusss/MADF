# Git Recovery Strategy - BMAD Files Protected

## ✅ SAFETY CHECKPOINT COMPLETED

**Commit:** `f5c396e` - "SAFETY BACKUP: Track all BMAD and project files before any operations"
**Status:** All previously untracked files now recoverable via git
**Files Protected:** 403 files including complete `.bmad-core/` and `.claude/` infrastructure

## Recovery Commands

### Restore BMAD Files if Accidentally Deleted
```bash
# Restore complete .bmad-core directory
git checkout HEAD -- .bmad-core/

# Restore specific BMAD file
git checkout HEAD -- .bmad-core/agents/pm.md

# Restore .claude commands that were deleted earlier
git checkout HEAD -- .claude/commands/BMad/
```

### Emergency Recovery from Any Point
```bash
# See all commits with file changes
git log --name-status --oneline -10

# Restore entire project from safety checkpoint
git checkout f5c396e -- .

# Create recovery branch from safety checkpoint
git checkout -b recovery-branch f5c396e
```

### Before Any Destructive Operation (MANDATORY)
```bash
# Create checkpoint before ANY risky operation
git add -A
git commit -m "Pre-operation checkpoint: about to [SPECIFIC ACTION]"

# Example: Before deleting or refactoring
git add -A
git commit -m "Pre-refactor checkpoint: removing BMAD dependencies from Story 1.1"
```

## Repository Setup for Remote Backup

### Create GitHub Repository
```bash
# Create new repository
gh repo create MADF --private --description "Multi-Agent Development Framework"

# Add remote and push
git remote add origin https://github.com/[username]/MADF.git
git push -u origin master
```

### Alternative: Manual Remote Setup
```bash
# Add existing GitHub repo as remote
git remote add origin [your-github-repo-url]
git push -u origin master
```

## Best Practices Now Implemented

### ✅ Track Everything Strategy
- All BMAD files (`.bmad-core/`) now tracked
- All Claude infrastructure (`.claude/`) now tracked
- All documentation and project files now tracked
- No critical files left untracked

### ✅ Recovery-First Workflow
- Safety commit exists before any major operations
- All files recoverable via `git checkout HEAD -- [path]`
- Complete project state preserved in git history

### ✅ Destructive Action Prevention
- Added color-coded risk system to `.claude/output-styles/madf-communication.md`
- RED operations require explicit confirmation
- Ambiguity detection for high-risk terms

## File Recovery Examples

```bash
# If BMAD gets deleted again:
git checkout HEAD -- .bmad-core/

# If .claude/commands/BMad gets deleted:
git checkout HEAD -- .claude/commands/BMad/

# If entire project gets corrupted:
git reset --hard f5c396e

# If need to see what was deleted:
git diff HEAD~1 --name-status
```

## Next Steps

1. **Set up remote repository** for offsite backup
2. **Create regular checkpoint commits** before major operations
3. **Follow RED operation protocols** for any destructive commands
4. **Test recovery procedures** to ensure they work

## Summary

**Problem:** BMAD files were untracked and got deleted without recovery option
**Solution:** All files now tracked in git commit `f5c396e`
**Protection:** Can recover any file/directory from this checkpoint
**Prevention:** Destructive action rules implemented in communication standards

**RESULT:** Never lose critical files again - everything is recoverable via git.