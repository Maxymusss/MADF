# Testing Standards

## CRITICAL: No Mock Tests Policy

**ABSOLUTE RULE**: All tests MUST use real implementations, NOT mocks

### Prohibited Practices
- ❌ Mock implementations that return hardcoded data
- ❌ `unittest.mock.Mock`, `unittest.mock.AsyncMock`, `unittest.mock.MagicMock`
- ❌ `@patch` decorators that replace real functionality
- ❌ Fake/stub implementations in test files
- ❌ Tests that pass without validating actual functionality

### Required Practices
- ✅ Real database connections (Neo4j, PostgreSQL) with test databases
- ✅ Real MCP server connections with test configurations
- ✅ Real API calls with test credentials or sandboxed environments
- ✅ Real file operations with temporary test directories
- ✅ Real network calls to actual services (with test accounts)

## Test Environment Configuration

### Test Database Setup
```python
# CORRECT: Real Neo4j test database
@pytest.fixture
def neo4j_test_db():
    """Real Neo4j database for testing"""
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_TEST_URI", "bolt://localhost:7687"),
        auth=(os.getenv("NEO4J_TEST_USER"), os.getenv("NEO4J_TEST_PASSWORD"))
    )
    # Setup test data
    yield driver
    # Cleanup test data
    driver.close()

# WRONG: Mock database
@pytest.fixture
def neo4j_test_db():
    mock_db = MagicMock()
    mock_db.query.return_value = {"fake": "data"}
    return mock_db
```

### Test MCP Server Setup
```python
# CORRECT: Real MCP server connection
@pytest.fixture
async def graphiti_client():
    """Real Graphiti MCP client"""
    client = GraphitiClient()
    await client.initialize()
    yield client
    await client.close()

# WRONG: Mock MCP client
@pytest.fixture
def graphiti_client():
    mock_client = AsyncMock()
    mock_client.add_episode = AsyncMock(return_value={"fake": "episode"})
    return mock_client
```

### Test File Operations
```python
# CORRECT: Real filesystem operations with temp directory
@pytest.fixture
def test_workspace(tmp_path):
    """Real temporary directory for testing"""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    yield workspace
    # Cleanup handled by pytest tmp_path

# WRONG: Mock filesystem
@pytest.fixture
def test_workspace():
    mock_fs = MagicMock()
    mock_fs.read_file.return_value = "fake content"
    return mock_fs
```

## Test Data Management

### Use Real Test Data
- Create actual test databases (e.g., `madf_test` database)
- Use real test accounts with sandboxed/limited permissions
- Populate test data in setup, clean up in teardown
- Use transactions for isolated test execution

### Environment Variables for Testing
```bash
# .env.test
NEO4J_TEST_URI=bolt://localhost:7687
NEO4J_TEST_USER=neo4j
NEO4J_TEST_PASSWORD=test_password
OPENAI_TEST_API_KEY=sk-test-...
OBSIDIAN_TEST_API_KEY=test_api_key_...
FILESYSTEM_TEST_ALLOWED_DIRS=/tmp/madf_test
```

## Test Isolation

### Transaction-Based Isolation
```python
@pytest.fixture
async def isolated_db_session():
    """Real database with transaction rollback"""
    async with db_engine.begin() as conn:
        yield conn
        await conn.rollback()  # Rollback after each test
```

### Temporary Resources
```python
@pytest.fixture
def temp_obsidian_vault(tmp_path):
    """Real temporary Obsidian vault"""
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()
    # Create real vault structure
    (vault_path / ".obsidian").mkdir()
    yield vault_path
    # Cleanup handled by pytest
```

## When Real Testing is Impractical

### Cost-Prohibitive APIs
If API calls cost money per request:
1. Use sandbox/test tier of the service
2. Use rate-limited test accounts
3. Use VCR.py to record/replay real responses (NOT mocks)
4. Document why real testing isn't feasible

### External Service Unavailability
If service requires manual setup:
1. Document setup requirements in test README
2. Skip tests with clear message: `@pytest.mark.skipif(not has_service(), reason="Service not available")`
3. Provide docker-compose for local service setup
4. Use CI/CD with real service instances

## Test Coverage Requirements

### Minimum Coverage by Type
- **Unit Tests**: 70% coverage with real implementations
- **Integration Tests**: 25% coverage with real service connections
- **End-to-End Tests**: 5% coverage with full stack

### Critical Path Testing
- All MCP integrations MUST have real connection tests
- All database operations MUST use real test databases
- All file operations MUST use real filesystem with temp directories
- All API calls MUST use real test endpoints

## Test Naming Convention

```python
# Format: test_<component>_<scenario>_<expected_behavior>

def test_graphiti_add_episode_creates_node():
    """REAL test: Creates actual node in Neo4j test database"""
    pass

def test_filesystem_read_file_returns_content():
    """REAL test: Reads actual file from temp directory"""
    pass

def test_knowledge_agent_stores_episode_in_graph():
    """REAL test: Stores episode in real Graphiti Neo4j instance"""
    pass
```

## Test Failure Debugging

### Real Tests Provide Real Errors
```python
# REAL test shows actual error
def test_graphiti_connection():
    client = GraphitiClient()
    # This will fail with real Neo4j connection error
    # Helps identify: credentials, network, service availability
    result = await client.initialize()
    assert result.connected == True

# MOCK test hides real issues
def test_graphiti_connection_WRONG():
    mock_client = MagicMock()
    mock_client.initialize.return_value = {"connected": True}
    # Always passes, never validates real connectivity
    result = mock_client.initialize()
    assert result["connected"] == True
```

## Enforcement

### Pre-commit Checks
- Reject commits containing `unittest.mock` imports in test files
- Require real environment setup documentation
- Validate test coverage with real implementations

### Code Review Requirements
- All test PRs must demonstrate real service integration
- Tests using mocks will be rejected
- Test configuration must use real credentials/connections

## Migration from Mock Tests

### Existing Mock Tests
All current mock tests in `tests/test_story_1_*.py` MUST be replaced with real implementations:

1. **Identify mock usage**: Search for `Mock`, `AsyncMock`, `MagicMock`, `@patch`
2. **Create real test fixtures**: Setup real services (Neo4j, Obsidian, Filesystem)
3. **Replace mock assertions**: Use real service responses
4. **Validate behavior**: Ensure tests catch actual integration issues

### Priority Order
1. Story 1.3 Knowledge Agent tests (Graphiti, Obsidian, Filesystem)
2. Story 1.2 Analyst Agent tests (Context7, Sequential Thinking)
3. Story 1.1 Core Architecture tests (LangGraph, MCP Bridge)

## Documentation Requirements

### Test README
Each test file MUST include setup instructions:

```markdown
# Story 1.3 Knowledge Agent Tests

## Prerequisites
- Neo4j 5.26+ running on bolt://localhost:7687
- Obsidian with Local REST API plugin enabled
- Valid OPENAI_API_KEY for Graphiti embeddings

## Setup
\```bash
# Start Neo4j test database
docker run -p 7687:7687 -e NEO4J_AUTH=neo4j/test_password neo4j:5.26

# Configure Obsidian test vault
cp .env.test.example .env.test
# Add OBSIDIAN_TEST_API_KEY to .env.test

# Run tests
pytest tests/test_story_1_3_knowledge_agent.py
\```

## Cleanup
Tests automatically clean up after execution using fixtures.
```

## Rationale

### Why No Mocks?

1. **Mock tests pass with broken code**: Tests validate mock behavior, not real functionality
2. **Integration issues hidden**: Real service connection problems never discovered
3. **False confidence**: 100% mock test coverage != working system
4. **Maintenance burden**: Mocks need updates when APIs change, but don't catch breaking changes
5. **Production failures**: Mocks can't predict real-world edge cases and errors

### Real Tests Catch Real Issues

- Neo4j authentication failures
- MCP server connection timeouts
- API rate limits and quota exhaustion
- File permission errors
- Network connectivity issues
- Schema validation failures
- Version compatibility problems

**ABSOLUTE REQUIREMENT**: Every test MUST exercise real functionality to provide genuine validation of system behavior.