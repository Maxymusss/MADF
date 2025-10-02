# Real test fixtures for Story 1.3 - NO MOCKS
# Uses actual Neo4j, Obsidian, and Filesystem connections

import os
import sys
import pytest
import pytest_asyncio
import asyncio
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root .env
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Add project root to Python path
sys.path.insert(0, str(project_root / "src"))

from core.mcp_bridge import MCPBridge
from agents.knowledge_agent import KnowledgeAgent


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_env_vars():
    """Validate required environment variables from .env"""
    required_vars = {
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USER": os.getenv("NEO4J_USER"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }

    missing = [k for k, v in required_vars.items() if not v or v.startswith("your_")]
    if missing:
        pytest.skip(f"Missing required environment variables in .env: {', '.join(missing)}")

    return required_vars


@pytest_asyncio.fixture
async def neo4j_test_db(test_env_vars):
    """
    Real Neo4j test database connection

    Setup: Creates test database
    Teardown: Cleans up test data
    """
    try:
        from neo4j import GraphDatabase
    except ImportError:
        pytest.skip("neo4j driver not installed: pip install neo4j")

    driver = GraphDatabase.driver(
        test_env_vars["NEO4J_URI"],
        auth=(test_env_vars["NEO4J_USER"], test_env_vars["NEO4J_PASSWORD"])
    )

    # Verify connection
    try:
        driver.verify_connectivity()
    except Exception as e:
        pytest.skip(f"Cannot connect to Neo4j test database: {e}")

    yield driver

    # Cleanup: Delete all test nodes
    with driver.session() as session:
        session.run("MATCH (n) WHERE n.test_marker = 'madf_test' DETACH DELETE n")

    driver.close()


@pytest_asyncio.fixture
async def mcp_bridge_instance(test_env_vars, neo4j_test_db):
    """
    MCPBridge instance for direct MCP tool calls

    Uses actual MCP servers (Graphiti, Obsidian, Filesystem)
    """
    # Environment variables already loaded from .env
    # Verify they are set correctly
    assert os.environ.get("NEO4J_URI") == test_env_vars["NEO4J_URI"]
    assert os.environ.get("NEO4J_USER") == test_env_vars["NEO4J_USER"]
    assert os.environ.get("NEO4J_PASSWORD") == test_env_vars["NEO4J_PASSWORD"]
    assert os.environ.get("OPENAI_API_KEY") == test_env_vars["OPENAI_API_KEY"]

    bridge = MCPBridge()

    # Verify Graphiti server config exists
    if "graphiti" not in bridge.direct_mcp_servers:
        pytest.skip("Graphiti MCP server not configured in mcp_bridge")

    yield bridge

    # MCPBridge manages its own cleanup


@pytest.fixture
def obsidian_test_vault(tmp_path):
    """
    Real temporary Obsidian vault for testing

    Creates actual vault directory structure
    """
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir()

    # Create Obsidian vault structure
    (vault_path / ".obsidian").mkdir()
    (vault_path / ".obsidian" / "config").write_text("{}")

    # Create some test notes
    (vault_path / "README.md").write_text("# Test Vault\n\nThis is a test vault.")

    notes_dir = vault_path / "Notes"
    notes_dir.mkdir()
    (notes_dir / "test_note.md").write_text("# Test Note\n\nSome content.")

    yield vault_path

    # Cleanup handled by pytest tmp_path


# Obsidian test vault fixture remains for filesystem setup
# No separate client needed - use mcp_bridge_instance directly


@pytest.fixture
def filesystem_test_workspace(tmp_path):
    """
    Real temporary filesystem workspace for testing

    Creates actual directory structure with test files
    """
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()

    # Create test directory structure
    src_dir = workspace / "src"
    src_dir.mkdir()
    (src_dir / "test_file.py").write_text("# Test Python file\nprint('hello')")

    docs_dir = workspace / "docs"
    docs_dir.mkdir()
    (docs_dir / "README.md").write_text("# Documentation\n\nTest docs.")

    tests_dir = workspace / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_sample.py").write_text("# Test file\nassert True")

    yield workspace

    # Cleanup handled by pytest tmp_path


# Filesystem test workspace fixture remains for directory setup
# No separate client needed - use mcp_bridge_instance directly


@pytest_asyncio.fixture
async def real_knowledge_agent(mcp_bridge_instance):
    """
    Real Knowledge Agent with direct MCP bridge integration

    No mocks - uses actual mcp_bridge for Graphiti, Obsidian, and Filesystem
    """
    agent = KnowledgeAgent()

    # Agent already uses mcp_bridge internally
    # No client replacement needed - architecture follows Story 1.2 pattern

    yield agent

    await agent.close()


@pytest.fixture
def test_episode_data():
    """Real test data for Graphiti episodes"""
    return {
        "content": "Test episode: User implemented filesystem MCP integration",
        "episode_type": "implementation",
        "source": "test_suite",
        "metadata": {
            "test_marker": "madf_test",
            "story": "1.3",
            "component": "knowledge_agent"
        }
    }


@pytest.fixture
def test_obsidian_note():
    """Real test data for Obsidian notes"""
    return {
        "file_path": "/test_notes/test_doc.md",
        "content": "# Test Documentation\n\n## Section 1\n\nTest content for knowledge agent.",
        "operation": "append"
    }


@pytest.fixture
def test_filesystem_paths(filesystem_test_workspace):
    """Real filesystem paths for testing"""
    return {
        "workspace": str(filesystem_test_workspace),
        "test_file": str(filesystem_test_workspace / "src" / "test_file.py"),
        "test_dir": str(filesystem_test_workspace / "docs"),
        "search_pattern": "*.py"
    }


# Helper functions for real testing
def verify_neo4j_connection(uri: str, user: str, password: str) -> bool:
    """Verify Neo4j is accessible"""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        driver.close()
        return True
    except Exception:
        return False


def verify_obsidian_api(host: str, port: str, api_key: str) -> bool:
    """Verify Obsidian REST API is accessible"""
    try:
        import requests
        response = requests.get(
            f"http://{host}:{port}/",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=2
        )
        return response.status_code in [200, 401, 403]  # Any response means API is running
    except Exception:
        return False