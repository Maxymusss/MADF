# Story 1.3 Real Integration Tests

**NO MOCKS** - All tests use real implementations: Neo4j, Obsidian REST API, Filesystem operations.

## Prerequisites

### Required Services

1. **Neo4j 5.26+** (for Graphiti tests)
   - Running on `bolt://localhost:7687`
   - Authentication: username/password
   - Test database: `madf_test`

2. **OpenAI API Key** (for Graphiti embeddings)
   - Valid API key starting with `sk-`
   - Used for semantic search in knowledge graphs

3. **Obsidian with Local REST API Plugin** (for Obsidian tests)
   - Obsidian app running
   - Local REST API plugin installed and enabled
   - API key generated
   - Listening on `127.0.0.1:27124`

4. **Filesystem Access** (for Filesystem tests)
   - Write permissions to `tests/fixtures/test_workspace`
   - Temp directory access

## Setup Instructions

### 1. Install Neo4j

**Docker (Recommended):**
```bash
docker run -d \
  --name neo4j-test \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/test_password \
  neo4j:5.26
```

**Manual Installation:**
1. Download Neo4j 5.26+ from https://neo4j.com/download/
2. Install and start Neo4j
3. Set password: `test_password`
4. Verify connection: http://localhost:7474

### 2. Configure OpenAI API Key

```bash
# Get API key from https://platform.openai.com/api-keys
export OPENAI_TEST_API_KEY=sk-your-actual-key-here
```

### 3. Setup Obsidian REST API

1. Install Obsidian: https://obsidian.md/download
2. Install Local REST API plugin:
   - Settings → Community Plugins → Browse
   - Search "Local REST API"
   - Install and Enable
3. Generate API key:
   - Settings → Local REST API → API Key
   - Copy API key
4. Verify API is running:
   ```bash
   curl http://127.0.0.1:27124/
   ```

### 4. Configure Test Environment

```bash
# Copy example environment file
cp tests/.env.test.example tests/.env.test

# Edit tests/.env.test with your credentials
# NEO4J_TEST_URI=bolt://localhost:7687
# NEO4J_TEST_USER=neo4j
# NEO4J_TEST_PASSWORD=test_password
# OPENAI_TEST_API_KEY=sk-your-key-here
# OBSIDIAN_TEST_API_KEY=your-obsidian-api-key
```

### 5. Install Python Dependencies

```bash
# Install Neo4j driver
pip install neo4j

# Install requests for Obsidian API
pip install requests

# Install pytest async support
pip install pytest-asyncio

# Install python-dotenv for environment loading
pip install python-dotenv
```

## Running Tests

### Run All Real Tests

```bash
# Run all Story 1.3 real tests
pytest tests/test_story_1_3_real_*.py -v

# Run with detailed output
pytest tests/test_story_1_3_real_*.py -v --tb=short
```

### Run Specific Test Categories

```bash
# Graphiti MCP tests only
pytest tests/test_story_1_3_real_graphiti.py -v

# Obsidian MCP tests only
pytest tests/test_story_1_3_real_obsidian.py -v

# Filesystem MCP tests only
pytest tests/test_story_1_3_real_filesystem.py -v

# Knowledge Agent tests only
pytest tests/test_story_1_3_real_knowledge_agent.py -v
```

### Run Specific Test

```bash
# Run single test
pytest tests/test_story_1_3_real_graphiti.py::TestTask1GraphitiMCPRealIntegration::test_graphiti_real_connection -v
```

### Skip Tests When Services Unavailable

Tests automatically skip when required services are unavailable:

```bash
# Tests will skip gracefully if Neo4j is not running
pytest tests/test_story_1_3_real_graphiti.py -v

# Output:
# SKIPPED - Cannot connect to Neo4j test database: [Errno 111] Connection refused
```

## Test Structure

### conftest_real.py
Real test fixtures loading from .env:
- Loads environment variables from `D:\dev\MADF\.env`
- `neo4j_test_db` - Real Neo4j database connection
- `real_graphiti_client` - Real Graphiti client with Neo4j
- `obsidian_test_vault` - Real temporary Obsidian vault
- `real_obsidian_client` - Real Obsidian REST API client
- `filesystem_test_workspace` - Real temp filesystem workspace
- `real_filesystem_client` - Real filesystem client
- `real_knowledge_agent` - Complete Knowledge Agent with all real clients

**Environment Loading:**
```python
from dotenv import load_dotenv
from pathlib import Path

project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)  # Loads NEO4J_URI, OPENAI_API_KEY, etc.
```

### Test Files

1. **test_story_1_3_real_graphiti.py** (13 tests)
   - Real Neo4j database connection
   - Episode storage and retrieval
   - Semantic search with OpenAI embeddings
   - Bi-temporal tracking
   - Error handling with invalid credentials
   - Concurrent operations

2. **test_story_1_3_real_obsidian.py** (12 tests)
   - Real vault file operations
   - Document creation and modification
   - Search across real notes
   - Content patching and appending
   - Error handling (read-only, non-existent files)
   - Concurrent file operations

3. **test_story_1_3_real_filesystem.py** (16 tests)
   - Real file read/write operations
   - Directory creation and listing
   - File searching with glob patterns
   - File moves and renames
   - Permission and safety checks
   - Large file handling
   - Concurrent operations

4. **test_story_1_3_real_knowledge_agent.py** (17 tests)
   - Complete Knowledge Agent with all 3 MCPs
   - Cross-session memory persistence
   - End-to-end workflows
   - Concurrent multi-client operations

**Total: 58 Real Tests (0 Mocks)**

## What These Tests Catch

Real tests catch issues mocks cannot:

### Neo4j/Graphiti Tests
- ✅ Invalid authentication credentials
- ✅ Network connection failures
- ✅ Neo4j version incompatibilities
- ✅ OpenAI API rate limits
- ✅ Embedding generation errors
- ✅ Concurrent write conflicts
- ✅ Database transaction failures

### Obsidian Tests
- ✅ REST API connection failures
- ✅ Invalid API keys
- ✅ File permission errors
- ✅ Vault structure issues
- ✅ Concurrent file access
- ✅ Special characters in filenames
- ✅ Large file handling

### Filesystem Tests
- ✅ Permission denied errors
- ✅ Disk space issues
- ✅ Path traversal attempts
- ✅ Read-only filesystem
- ✅ Concurrent file operations
- ✅ Symbolic link handling
- ✅ File locking

### Knowledge Agent Tests
- ✅ Client initialization failures
- ✅ Multi-client coordination
- ✅ Resource cleanup
- ✅ Memory leaks
- ✅ Deadlocks
- ✅ Error propagation

## Cleanup

Tests automatically clean up after themselves:

- **Neo4j**: Deletes test nodes with `test_marker='madf_test'`
- **Obsidian**: Uses temporary vault (pytest tmp_path)
- **Filesystem**: Uses temporary workspace (pytest tmp_path)

## CI/CD Integration

```yaml
# .github/workflows/test-real-story-1-3.yml
name: Story 1.3 Real Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      neo4j:
        image: neo4j:5.26
        env:
          NEO4J_AUTH: neo4j/test_password
        ports:
          - 7687:7687

    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install neo4j pytest-asyncio python-dotenv requests

      - name: Configure .env for tests
        run: |
          echo "NEO4J_URI=bolt://localhost:7687" >> .env
          echo "NEO4J_USER=neo4j" >> .env
          echo "NEO4J_PASSWORD=test_password" >> .env
          echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> .env

      - name: Run real tests
        run: pytest tests/test_story_1_3_real_*.py -v --tb=short
```

## Troubleshooting

### Neo4j Connection Errors

```bash
# Verify Neo4j is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs neo4j-test

# Test connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'test_password')); driver.verify_connectivity(); print('Connected!')"
```

### Obsidian API Errors

```bash
# Verify API is running
curl http://127.0.0.1:27124/

# Check Obsidian plugin settings
# Settings → Local REST API → Enable

# Test API key
curl -H "Authorization: Bearer YOUR_API_KEY" http://127.0.0.1:27124/
```

### Filesystem Permission Errors

```bash
# Check directory permissions
ls -la tests/fixtures/

# Create test workspace
mkdir -p tests/fixtures/test_workspace
chmod 755 tests/fixtures/test_workspace
```

## Migration from Mock Tests

Old mock tests in `test_story_1_3_knowledge_agent.py` are deprecated.
All new development uses real tests in `test_story_1_3_real_*.py` files.

**DO NOT** add new mock tests. All tests MUST use real implementations.