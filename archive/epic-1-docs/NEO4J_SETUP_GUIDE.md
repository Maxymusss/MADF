# Neo4j Setup Guide for MADF Testing

## Current Status

**Neo4j container `neo4j-madf` is already running:**
- Container: `neo4j:5.26`
- Ports: 7474 (HTTP), 7687 (Bolt)
- Authentication: neo4j / madf-dev-password
- Status: ✅ Connected and operational

## Verify Connection

```bash
# Test Neo4j connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'madf-dev-password')); driver.verify_connectivity(); print('Connected!'); driver.close()"
```

## Access Neo4j Browser

Open browser to: http://localhost:7474

**Login credentials:**
- Username: `neo4j`
- Password: `madf-dev-password`

## Test Database Setup

Tests use the same Neo4j instance but mark test data with `test_marker='madf_test'` for cleanup.

### Create Test Database (Optional)

If you want isolated test database:

```cypher
// In Neo4j Browser
CREATE DATABASE madf_test;
```

Then update tests/.env.test:
```bash
NEO4J_TEST_DATABASE=madf_test
```

### Verify Test Data Isolation

```cypher
// Find test data
MATCH (n) WHERE n.test_marker = 'madf_test'
RETURN n LIMIT 25;

// Clean up test data manually
MATCH (n) WHERE n.test_marker = 'madf_test'
DETACH DELETE n;
```

## Docker Commands

### View Container Status
```bash
docker ps | findstr neo4j
```

### View Container Logs
```bash
docker logs neo4j-madf
```

### Stop Container
```bash
docker stop neo4j-madf
```

### Start Container
```bash
docker start neo4j-madf
```

### Restart Container
```bash
docker restart neo4j-madf
```

### Remove Container (Caution: Deletes all data)
```bash
docker stop neo4j-madf
docker rm neo4j-madf
```

## Fresh Neo4j Installation

If you need to create a new Neo4j container:

```bash
# Stop and remove existing container
docker stop neo4j-madf
docker rm neo4j-madf

# Create new container
docker run -d \
  --name neo4j-madf \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/madf-dev-password \
  -v neo4j_data:/data \
  -v neo4j_logs:/logs \
  neo4j:5.26

# Wait for startup (30 seconds)
timeout /t 30

# Verify connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'madf-dev-password')); driver.verify_connectivity(); print('Connected!'); driver.close()"
```

## Authentication Failure Troubleshooting

### Issue: "Failed to establish connection"

**Cause:** Neo4j container not running

**Solution:**
```bash
docker start neo4j-madf
```

### Issue: "AuthError: The client is unauthorized"

**Cause:** Wrong password

**Solution 1 - Use correct password:**
```bash
# Update .env.test with correct password
NEO4J_TEST_PASSWORD=madf-dev-password
```

**Solution 2 - Reset Neo4j password:**
```bash
# Stop container
docker stop neo4j-madf

# Reset password via Docker
docker run -d \
  --name neo4j-madf-new \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your-new-password \
  neo4j:5.26
```

### Issue: "ServiceUnavailable: Unable to connect to localhost:7687"

**Cause:** Neo4j not listening on 7687

**Solution:**
```bash
# Check Neo4j is running
docker logs neo4j-madf | findstr "Started"

# Should see: "Started."
# If not, wait 30 seconds and check again

# Verify port is exposed
docker port neo4j-madf 7687
# Should output: 0.0.0.0:7687
```

### Issue: "ConnectionRefusedError: [Errno 111] Connection refused"

**Cause:** Firewall blocking port 7687

**Solution:**
```bash
# Windows Firewall
# Control Panel → Windows Defender Firewall → Advanced Settings
# New Inbound Rule → Port → TCP → 7687 → Allow

# Or use Docker Desktop network settings
```

## Test Real Authentication Failures

The real tests catch these errors:

```python
# Test invalid password
@pytest.mark.asyncio
async def test_graphiti_error_handling_real():
    """REAL TEST: Catches invalid Neo4j password"""
    os.environ["NEO4J_PASSWORD"] = "wrong_password"

    client = GraphitiClient()

    # This will raise AuthError from Neo4j
    with pytest.raises(Exception) as exc_info:
        await client.initialize()

    # Real error: "The client is unauthorized due to authentication failure."
    assert "unauthorized" in str(exc_info.value).lower()
```

**What mocks hide:**
- ✅ Wrong password → Mock returns fake success
- ✅ Neo4j down → Mock returns fake connection
- ✅ Network timeout → Mock returns instantly
- ✅ Version incompatibility → Mock ignores driver version

**What real tests catch:**
- ❌ Wrong password → AuthError raised
- ❌ Neo4j down → ServiceUnavailable raised
- ❌ Network timeout → Real timeout after 30s
- ❌ Version mismatch → Driver incompatibility error

## Python Neo4j Driver Installation

```bash
# Install Neo4j Python driver
pip install neo4j

# Verify installation
python -c "import neo4j; print(f'Neo4j driver version: {neo4j.__version__}')"
```

## Environment Variables Reference

**Production (.env):**
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=madf-dev-password
OPENAI_API_KEY=your_openai_api_key_here
```

**Testing (tests/.env.test):**
```bash
NEO4J_TEST_URI=bolt://localhost:7687
NEO4J_TEST_USER=neo4j
NEO4J_TEST_PASSWORD=madf-dev-password
OPENAI_TEST_API_KEY=your_openai_api_key_here
NEO4J_TEST_DATABASE=madf_test
```

## Running Tests with Real Neo4j

```bash
# Run Graphiti tests (requires Neo4j + OpenAI API key)
pytest tests/test_story_1_3_real_graphiti.py -v

# Tests will skip if Neo4j unavailable
# SKIPPED - Cannot connect to Neo4j test database

# Tests will fail if wrong password (catches real auth errors!)
# AuthError: The client is unauthorized due to authentication failure.
```

## Quick Start

**If Neo4j container already running (current state):**
```bash
# 1. Verify connection
docker ps | findstr neo4j

# 2. Update OpenAI API key in tests/.env.test
# OPENAI_TEST_API_KEY=sk-your-real-key-here

# 3. Run tests
pytest tests/test_story_1_3_real_graphiti.py -v
```

**If Neo4j not running:**
```bash
# 1. Start existing container
docker start neo4j-madf

# 2. Wait 30 seconds for startup
timeout /t 30

# 3. Verify connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'madf-dev-password')); driver.verify_connectivity(); print('Ready!'); driver.close()"

# 4. Run tests
pytest tests/test_story_1_3_real_graphiti.py -v
```

## Summary

✅ Neo4j container `neo4j-madf` running on ports 7474/7687
✅ Authentication working: neo4j / madf-dev-password
✅ Browser accessible: http://localhost:7474
✅ Tests configured in tests/.env.test
⚠️ Need valid OPENAI_API_KEY for Graphiti embeddings

**Next step:** Add real OpenAI API key to tests/.env.test and run tests.