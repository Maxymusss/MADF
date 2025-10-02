# MADF Test Suite

## Directory Structure

```
tests/
├── reports/                     # All test reports and coverage data
│   └── test_report_story_*.md  # Story-specific test reports
├── test_story_*_*.py           # Story test files
└── README.md                   # This file
```

## Testing Conventions

### Test Organization
- **Test Files**: Named `test_story_{epic}_{story}_{description}.py`
- **Test Classes**: Group related tests by component
- **Test Methods**: Descriptive names starting with `test_`

### Test Reports
- **Location**: All test reports MUST be saved in `tests/reports/`
- **Naming**: `test_report_story_{epic}_{story}.md` or `test_report_{date}.md`
- **Format**: Markdown with sections for summary, results, coverage

### Running Tests

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific story tests
uv run python -m pytest tests/test_story_1_1_*.py -v

# Generate test report
uv run python -m pytest tests/ -v --tb=short > tests/reports/test_report_$(date +%Y%m%d).md
```

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Multi-component interaction
3. **System Tests**: End-to-end workflow validation

### TDD Workflow
1. **RED**: Write failing tests first
2. **GREEN**: Implement code to pass tests
3. **REFACTOR**: Improve code while maintaining green tests

## Current Test Coverage

| Story | Tests | Status | Report |
|-------|-------|--------|--------|
| 1.1 Core Architecture | 20/20 | ✅ PASSED | [View Report](reports/test_report_story_1_1.md) |
| 1.2a MCP-use Loader | Pending | ⏳ | - |
| 1.2b Chrome DevTools | Pending | ⏳ | - |

## Test Execution Policy
- All stories MUST have comprehensive test coverage
- Test reports MUST be generated and saved in `tests/reports/`
- Tests MUST pass before story is marked complete
- TDD approach is REQUIRED for all implementations