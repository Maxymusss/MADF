# Testing Conventions for MADF

## CRITICAL: No Mock Tests Policy

**ABSOLUTE RULE**: All tests MUST use real implementations, NOT mocks

### Prohibited Practices
- ❌ Mock implementations returning hardcoded data
- ❌ `unittest.mock.Mock`, `unittest.mock.AsyncMock`, `unittest.mock.MagicMock`
- ❌ `@patch` decorators replacing real functionality
- ❌ Fake/stub implementations in test files
- ❌ Tests passing without validating actual functionality

### Required Practices
- ✅ Real database connections (Neo4j, PostgreSQL) with test databases
- ✅ Real MCP server connections with test configurations
- ✅ Real API calls with test credentials or sandboxed environments
- ✅ Real file operations with temporary test directories (`pytest.tmp_path`)
- ✅ Real network calls to actual services (with test accounts)

### Rationale
- Mock tests pass with broken code, hiding integration issues until production
- False confidence from 100% mock coverage doesn't validate real functionality
- Real tests catch: auth failures, connection timeouts, rate limits, permission errors, version incompatibilities
- Mocks require maintenance when APIs change but don't catch breaking changes

### Test Environment Setup
```bash
# .env.test - Required for real testing
NEO4J_TEST_URI=bolt://localhost:7687
NEO4J_TEST_USER=neo4j
NEO4J_TEST_PASSWORD=test_password
OPENAI_TEST_API_KEY=sk-test-...
OBSIDIAN_TEST_API_KEY=test_api_key_...
FILESYSTEM_TEST_ALLOWED_DIRS=/tmp/madf_test
```

### Exception Handling
If real testing is genuinely impractical (cost-prohibitive APIs):
1. Use sandbox/test tier of service
2. Use VCR.py to record/replay real responses (NOT mocks)
3. Document why real testing isn't feasible in test README
4. Skip with clear message: `@pytest.mark.skipif(not has_service(), reason="Service unavailable")`

**ENFORCEMENT**: Code reviews reject tests using mocks. All mock tests MUST be replaced with real implementations.

### Test Sample Output Requirement

**MANDATORY**: When running tests, ALWAYS provide sample output showing actual test results.

**Required Format:**
```bash
# Run tests with verbose output
uv run python -m pytest tests/test_*.py -v --tb=short

# Example output to include in documentation:
============================= test session starts =============================
tests/test_story_1_2_real_analyst_agent.py::TestTask1::test_serena_tool_loading PASSED
tests/test_story_1_2_real_analyst_agent.py::TestTask1::test_find_symbol_on_real_file PASSED
============================= 27 passed in 0.06s ==============================
```

**Reference Examples:**
- Story 1.2 Real Tests: `tests/test_story_1_2_real_analyst_agent.py` - See `tests/reports/test_report_story_1_2_real.md` for sample output
- Story 1.3 Real Tests: `tests/test_story_1_3_real_filesystem.py` - Sample outputs in test reports directory

**Why Sample Outputs Matter:**
- Proves tests actually execute (not just syntax-valid)
- Shows real execution time and pass/fail status
- Documents expected behavior with concrete evidence
- Helps debug when tests fail in different environments

---

## MANDATORY RULE: Test Report Location

**All test reports, coverage data, and testing artifacts MUST be saved in the `tests/` directory structure:**

```
tests/
├── reports/              # Test execution reports
├── coverage/             # Coverage data and reports
├── fixtures/             # Test fixtures and mock data
└── *.py                  # Test files
```

## Test Report Standards

### Location Requirements
- **Test Reports**: `tests/reports/test_report_*.md`
- **Coverage Reports**: `tests/coverage/coverage_*.html`
- **Performance Reports**: `tests/reports/perf_*.json`

### Naming Conventions
- Story Reports: `test_report_story_{epic}_{story}.md`
- Daily Reports: `test_report_{YYYYMMDD}.md`
- Coverage: `coverage_story_{epic}_{story}.html`

### Report Generation Commands
```bash
# Generate markdown report in correct location
uv run python -m pytest tests/ -v --tb=short > tests/reports/test_report_$(date +%Y%m%d).md

# Generate HTML coverage report
uv run python -m pytest tests/ --cov=src --cov-report html:tests/coverage/
```

## Test File Organization

### Test File Naming
- Unit tests: `test_unit_{component}.py`
- Integration tests: `test_integration_{feature}.py`
- Story tests: `test_story_{epic}_{story}_{component}.py`

### Test Class Structure
```python
class Test{ComponentName}:
    """Test {component description}"""

    def test_{specific_behavior}(self):
        """Test that {expected behavior}"""
        pass
```

## TDD Requirements

### Workflow
1. **Write Tests First**: Create comprehensive test suite before implementation
2. **Run Tests (RED)**: Confirm tests fail initially
3. **Implement Code**: Write minimal code to pass tests
4. **Run Tests (GREEN)**: Verify all tests pass
5. **Generate Report**: Save report to `tests/reports/`
6. **Refactor**: Improve code while maintaining green tests

### Coverage Requirements
- Minimum 80% code coverage for story completion
- 100% coverage for critical path components
- Coverage reports saved to `tests/coverage/`

## Enforcement
- **Developer Agent**: Automatically saves reports to `tests/reports/`
- **Validator Agent**: Checks reports exist in correct location
- **CI/CD**: Rejects commits with reports outside `tests/` directory

## Migration
- Any existing test reports in project root should be moved to `tests/reports/`
- Update references in documentation to new locations