# MADF Task Completion Workflow

## When a Task is Completed

### 1. Code Quality Checks
```bash
# Format code
black .

# Lint code  
flake8 .

# Type checking
mypy .
```

### 2. Testing
```bash
# Run full test suite
pytest

# Run specific story tests
python run_story_1_1_tests.py

# Run verification tests  
python verify_story_1_1.py

# Windows-compatible simple test
python simple_test.py
```

### 3. Dependency Management
```bash
# Sync Python dependencies
uv sync

# Install missing Node.js dependencies
npm install

# Verify MCP integration
npm list mcp-use
```

### 4. Framework Health Checks
```bash
# System health check
npm run health-check

# Tool status
npm run tool-stats

# Update tools if needed
npm run update-tools
```

### 5. Agent Workspace Cleanup
```bash
# Check agent communication files
ls agent_workspace/tasks/
ls agent_workspace/results/
ls agent_workspace/logs/

# Clean old files if needed (manual review)
```

### 6. Performance Verification
```bash
# Test main framework
python run_multi_agent_framework.py

# Test individual agents
python agents/product_manager_agent.py
```

### 7. Documentation Updates
- Update relevant README files if architecture changed
- Update memory files via Serena if significant changes
- Check `.claude/` configuration if tool usage changed

### 8. Version Control
```bash
# Check status
git status

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Descriptive commit message"

# Push if appropriate
git push
```

## Error Handling Checklist
- [ ] All agent errors logged to `agent_workspace/logs/`
- [ ] MCP tool failures handled gracefully
- [ ] Windows compatibility maintained (file paths, encodings)
- [ ] Timeout mechanisms working for long-running operations
- [ ] Fallback strategies available for critical failures

## Performance Criteria
- Task completion: 2-5 minutes per research session
- Sources per session: 10-20 reliable sources  
- Confidence score: 0.6-0.8 for well-sourced topics
- Error rate: <10% timing errors, <5% fact conflicts

## Success Metrics to Track
- Development velocity: Features delivered per month
- Code reuse: Component sharing across projects
- Agent performance: Trust score >70 within 2 months
- Cost efficiency: Framework cost <30% of time savings

## Abort Criteria (Review Triggers)
- Month 2: ROI <25% triggers scope reduction
- Month 3: ROI <50% triggers framework redesign  
- Any time: Budget overrun >3x triggers immediate review