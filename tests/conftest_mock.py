# pytest configuration and fixtures for MADF test environment
# CRITICAL DEVELOPMENT BLOCKER RESOLUTION
# Created: 2025-09-21 | Required for all story development

import os
import sys
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_env_setup():
    """Set up isolated test environment for each test."""
    # Create temporary test directories
    test_base = tempfile.mkdtemp(prefix="madf_test_")
    test_dirs = {
        'message_dir': Path(test_base) / "messages",
        'log_dir': Path(test_base) / "logs",
        'cache_dir': Path(test_base) / "cache",
        'state_dir': Path(test_base) / "state"
    }

    # Create directory structure
    for dir_path in test_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
        # Create subdirectories for agents
        for agent in ['pm', 'research1', 'research2', 'validator']:
            (dir_path / agent).mkdir(exist_ok=True)

    # Set test environment variables
    test_env = {
        'MESSAGE_DIR': str(test_dirs['message_dir']),
        'LOG_DIR': str(test_dirs['log_dir']),
        'CACHE_DIR': str(test_dirs['cache_dir']),
        'STATE_DIR': str(test_dirs['state_dir']),
        'ANTHROPIC_API_KEY': 'test_key_sk-ant-test',
        'ALPHA_VANTAGE_API_KEY': 'test_alpha_key',
        'IEX_CLOUD_API_TOKEN': 'test_iex_token',
        'NEWSAPI_ORG_KEY': 'test_news_key',
        'MOCK_EXTERNAL_APIS': 'true',
        'LOG_LEVEL': 'DEBUG',
        'MESSAGE_POLL_INTERVAL': '0.1',  # Faster for tests
        'CACHE_TTL_SECONDS': '10',       # Shorter for tests
        'MAX_RETRY_ATTEMPTS': '2'        # Fewer retries for tests
    }

    # Apply environment variables
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield {
        'dirs': test_dirs,
        'base': test_base,
        'env': test_env
    }

    # Cleanup
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value

    shutil.rmtree(test_base, ignore_errors=True)

@pytest.fixture
def sample_market_data():
    """Sample financial market data for testing."""
    return {
        "forex": {
            "USD/JPY": {
                "price": 150.25,
                "change": "+0.15%",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "alpha_vantage"
            },
            "EUR/USD": {
                "price": 1.0821,
                "change": "-0.08%",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "alpha_vantage"
            },
            "GBP/USD": {
                "price": 1.2634,
                "change": "+0.12%",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "alpha_vantage"
            }
        },
        "interest_rates": {
            "USD": {"rate": 5.50, "change": "+0.25", "meeting_date": "2024-12-18"},
            "EUR": {"rate": 3.75, "change": "0.00", "meeting_date": "2024-12-14"},
            "JPY": {"rate": 0.25, "change": "+0.15", "meeting_date": "2024-12-19"}
        }
    }

@pytest.fixture
def sample_news_data():
    """Sample financial news data for testing."""
    base_time = datetime.utcnow()
    return {
        "articles": [
            {
                "title": "Fed Signals Pause in Rate Hikes as Inflation Cools",
                "description": "Federal Reserve officials indicate potential pause in monetary tightening",
                "url": "https://example.com/fed-signals-pause",
                "publishedAt": (base_time - timedelta(hours=2)).isoformat(),
                "source": {"name": "Financial Times"},
                "relevance": "high",
                "sentiment": "neutral",
                "markets": ["USD", "interest_rates"]
            },
            {
                "title": "Bank of Japan Maintains Ultra-Loose Policy",
                "description": "BoJ keeps interest rates near zero despite global tightening",
                "url": "https://example.com/boj-maintains-policy",
                "publishedAt": (base_time - timedelta(hours=6)).isoformat(),
                "source": {"name": "Reuters"},
                "relevance": "high",
                "sentiment": "dovish",
                "markets": ["JPY", "USD/JPY"]
            },
            {
                "title": "EUR/USD Struggles Near Parity as ECB Concerns Mount",
                "description": "European Central Bank faces challenging economic outlook",
                "url": "https://example.com/eur-usd-parity",
                "publishedAt": (base_time - timedelta(hours=12)).isoformat(),
                "source": {"name": "Bloomberg"},
                "relevance": "medium",
                "sentiment": "bearish",
                "markets": ["EUR", "EUR/USD"]
            }
        ]
    }

@pytest.fixture
def sample_agent_messages():
    """Sample inter-agent messages for testing communication protocol."""
    timestamp = datetime.utcnow().isoformat()
    return {
        "task_assignment": {
            "message_id": "pm_001",
            "from": "product_manager",
            "to": "research_agent_1",
            "type": "task_assignment",
            "timestamp": timestamp,
            "content": {
                "task_type": "market_research",
                "focus": "Asia/G10 forex",
                "timeframe": "this_week",
                "priority": "high",
                "deadline": (datetime.utcnow() + timedelta(hours=2)).isoformat()
            }
        },
        "research_result": {
            "message_id": "ra1_001",
            "from": "research_agent_1",
            "to": "product_manager",
            "type": "research_result",
            "timestamp": timestamp,
            "content": {
                "task_id": "pm_001",
                "status": "completed",
                "data": {
                    "currency_pairs": ["USD/JPY", "EUR/USD"],
                    "key_findings": ["Fed pause signals", "BoJ maintains policy"],
                    "confidence_score": 0.85
                },
                "sources": ["alpha_vantage", "newsapi"]
            }
        },
        "validation_request": {
            "message_id": "pm_002",
            "from": "product_manager",
            "to": "validator_agent",
            "type": "validation_request",
            "timestamp": timestamp,
            "content": {
                "research_results": ["ra1_001", "ra2_001"],
                "validation_type": "cross_reference",
                "priority": "high"
            }
        }
    }

@pytest.fixture
def mock_mcp_servers():
    """Mock MCP servers for testing without external API calls."""
    alpha_vantage_mock = AsyncMock()
    alpha_vantage_mock.get_forex_data = AsyncMock(return_value={
        "USD/JPY": {"price": 150.25, "change": "+0.15%"}
    })

    newsapi_mock = AsyncMock()
    newsapi_mock.search_news = AsyncMock(return_value={
        "articles": [{"title": "Test News", "content": "Test content"}]
    })

    iex_cloud_mock = AsyncMock()
    iex_cloud_mock.get_forex_data = AsyncMock(return_value={
        "EUR/USD": {"price": 1.0821, "change": "-0.08%"}
    })

    return {
        'alpha_vantage': alpha_vantage_mock,
        'newsapi': newsapi_mock,
        'iex_cloud': iex_cloud_mock
    }

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing without API costs."""
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=MagicMock(
        content=[MagicMock(text="Mock LLM response for testing")]
    ))
    return mock_client

# Test data utilities
def create_test_message_file(message_dir: Path, message: dict, filename: str = None):
    """Helper to create message files for testing."""
    if filename is None:
        filename = f"{message['message_id']}.json"

    filepath = message_dir / filename
    with open(filepath, 'w') as f:
        json.dump(message, f, indent=2)
    return filepath

def cleanup_test_messages(message_dir: Path):
    """Helper to clean up test message files."""
    for file_path in message_dir.glob("*.json"):
        file_path.unlink()

# Async test helpers
async def wait_for_message_file(message_dir: Path, message_id: str, timeout: float = 5.0):
    """Wait for a message file to appear during testing."""
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < timeout:
        message_file = message_dir / f"{message_id}.json"
        if message_file.exists():
            with open(message_file) as f:
                return json.load(f)
        await asyncio.sleep(0.1)
    raise TimeoutError(f"Message {message_id} not found within {timeout} seconds")

# Performance testing utilities
@pytest.fixture
def performance_monitor():
    """Monitor for performance testing."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.memory_usage = []

        def start(self):
            self.start_time = datetime.utcnow()

        def stop(self):
            if self.start_time:
                return (datetime.utcnow() - self.start_time).total_seconds()
            return 0

        def check_memory_increase(self, baseline_mb: float, max_increase_percent: float = 20):
            """Check if memory usage is within acceptable limits."""
            # This would integrate with actual memory monitoring in real implementation
            return True  # Placeholder for MVP

    return PerformanceMonitor()

# Integration test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.performance = pytest.mark.performance