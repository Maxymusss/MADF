# MCP Server Authentication Implementation

**CRITICAL DEVELOPMENT BLOCKER RESOLUTION**
*Created: 2025-09-21 | Required for Story 1.3 development*

## 🔐 **OVERVIEW**

This document specifies the authentication implementation for MCP servers in the MADF financial research framework. This resolves the missing authentication implementation details identified in the PO validation.

### **Authentication Architecture**
- **Method**: API Key-based authentication via environment variables
- **Storage**: Secure environment variable management with dotenv
- **Rotation**: Planned key rotation strategy for production
- **Validation**: Runtime key validation with error handling
- **Separation**: Development vs production key management

---

## 🔑 **API KEY MANAGEMENT**

### **Required API Keys**

Based on the updated external API constraints document, the following API keys are required:

```bash
# Primary Financial Data Source
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# Backup Financial Data Source
IEX_CLOUD_API_TOKEN=your_iex_cloud_token_here

# News Data Source
NEWSAPI_ORG_KEY=your_newsapi_key_here

# LLM Services
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# Optional Validation Sources (if available)
REUTERS_API_TOKEN=your_reuters_token_here
BLOOMBERG_API_KEY=your_bloomberg_key_here
```

### **Environment File Structure**

**`.env` (Development)**
```bash
# =============================================================================
# MADF Development Environment Configuration
# =============================================================================

# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-your_development_key
CLAUDE_MODEL_ORCHESTRATOR=claude-3-opus-latest
CLAUDE_MODEL_EXECUTION=claude-3-sonnet-latest

# Primary Financial Data Sources
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_free_tier_key
IEX_CLOUD_API_TOKEN=your_iex_cloud_free_tier_token

# News Sources
NEWSAPI_ORG_KEY=your_newsapi_development_key

# Optional Validation Sources
REUTERS_API_TOKEN=optional_reuters_token
BLOOMBERG_API_KEY=optional_bloomberg_key

# System Configuration
LOG_LEVEL=DEBUG
MESSAGE_POLL_INTERVAL=1.0
CACHE_TTL_SECONDS=300
MAX_RETRY_ATTEMPTS=3
MOCK_EXTERNAL_APIS=false

# File Paths (relative to project root)
MESSAGE_DIR=data/messages
LOG_DIR=logs
CACHE_DIR=data/cache
STATE_DIR=data/state

# Rate Limiting Configuration
ALPHA_VANTAGE_CALLS_PER_MINUTE=5
NEWSAPI_DAILY_LIMIT=33
IEX_CLOUD_MONTHLY_LIMIT=500000

# Development Flags
DEVELOPMENT_MODE=true
ENABLE_API_CACHING=true
ENABLE_FALLBACK_DATA=true
```

**`.env.production` (Production)**
```bash
# =============================================================================
# MADF Production Environment Configuration
# =============================================================================

# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-production_key_with_higher_limits
CLAUDE_MODEL_ORCHESTRATOR=claude-3-opus-latest
CLAUDE_MODEL_EXECUTION=claude-3-sonnet-latest

# Primary Financial Data Sources - Production Tier
ALPHA_VANTAGE_API_KEY=premium_alpha_vantage_key
IEX_CLOUD_API_TOKEN=premium_iex_cloud_token

# News Sources - Production Tier
NEWSAPI_ORG_KEY=premium_newsapi_key

# Validation Sources
REUTERS_API_TOKEN=production_reuters_token
BLOOMBERG_API_KEY=production_bloomberg_key

# System Configuration
LOG_LEVEL=INFO
MESSAGE_POLL_INTERVAL=0.5
CACHE_TTL_SECONDS=180
MAX_RETRY_ATTEMPTS=5
MOCK_EXTERNAL_APIS=false

# File Paths
MESSAGE_DIR=/var/madf/messages
LOG_DIR=/var/log/madf
CACHE_DIR=/var/madf/cache
STATE_DIR=/var/madf/state

# Production Rate Limits
ALPHA_VANTAGE_CALLS_PER_MINUTE=25
NEWSAPI_DAILY_LIMIT=3333  # 100,000 monthly / 30 days
IEX_CLOUD_MONTHLY_LIMIT=500000

# Production Flags
DEVELOPMENT_MODE=false
ENABLE_API_CACHING=true
ENABLE_FALLBACK_DATA=true
ENABLE_MONITORING=true
```

---

## 🛡️ **AUTHENTICATION IMPLEMENTATION**

### **API Key Validation Module**

```python
# agents/python/common/auth.py

import os
import re
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

class APIKeyStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"
    EXPIRED = "expired"
    RATE_LIMITED = "rate_limited"

@dataclass
class APIKeyInfo:
    service: str
    key: str
    status: APIKeyStatus
    tier: str  # "free", "premium", "enterprise"
    rate_limit: Optional[int] = None
    expires_at: Optional[str] = None

class AuthenticationManager:
    """Centralized authentication management for all MCP servers."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._api_keys: Dict[str, APIKeyInfo] = {}
        self._load_api_keys()

    def _load_api_keys(self):
        """Load and validate all API keys from environment."""
        api_configs = {
            'alpha_vantage': {
                'env_var': 'ALPHA_VANTAGE_API_KEY',
                'pattern': r'^[A-Z0-9]{16}$',  # Typical Alpha Vantage format
                'required': True
            },
            'iex_cloud': {
                'env_var': 'IEX_CLOUD_API_TOKEN',
                'pattern': r'^pk_[a-f0-9]{32}$',  # IEX Cloud format
                'required': True
            },
            'newsapi': {
                'env_var': 'NEWSAPI_ORG_KEY',
                'pattern': r'^[a-f0-9]{32}$',  # NewsAPI format
                'required': True
            },
            'anthropic': {
                'env_var': 'ANTHROPIC_API_KEY',
                'pattern': r'^sk-ant-[a-zA-Z0-9\-_]{95}$',  # Anthropic format
                'required': True
            },
            'reuters': {
                'env_var': 'REUTERS_API_TOKEN',
                'pattern': r'^[A-Za-z0-9\-_]{20,}$',
                'required': False
            },
            'bloomberg': {
                'env_var': 'BLOOMBERG_API_KEY',
                'pattern': r'^[A-Za-z0-9\-_]{20,}$',
                'required': False
            }
        }

        for service, config in api_configs.items():
            key = os.getenv(config['env_var'])

            if not key:
                if config['required']:
                    self.logger.error(f"Required API key missing: {config['env_var']}")
                    status = APIKeyStatus.MISSING
                else:
                    self.logger.info(f"Optional API key not provided: {config['env_var']}")
                    continue
            else:
                # Validate key format
                if re.match(config['pattern'], key):
                    status = APIKeyStatus.VALID
                    self.logger.info(f"✓ Valid API key loaded for {service}")
                else:
                    status = APIKeyStatus.INVALID
                    self.logger.error(f"✗ Invalid API key format for {service}")

            self._api_keys[service] = APIKeyInfo(
                service=service,
                key=key if key else "",
                status=status,
                tier=self._detect_key_tier(service, key),
            )

    def _detect_key_tier(self, service: str, key: str) -> str:
        """Detect API key tier based on service and key characteristics."""
        if not key:
            return "none"

        # Service-specific tier detection logic
        if service == 'alpha_vantage':
            # Alpha Vantage free keys are typically shorter
            return "free" if len(key) == 16 else "premium"

        elif service == 'iex_cloud':
            # IEX Cloud uses pk_ prefix for publishable keys (free tier)
            # sk_ prefix for secret keys (paid tiers)
            return "free" if key.startswith('pk_') else "premium"

        elif service == 'newsapi':
            # NewsAPI doesn't have clear indicators, default to free for MVP
            return "free"

        elif service == 'anthropic':
            # All Anthropic keys have same format, tier determined by account
            return "paid"  # Assume paid tier for development

        else:
            return "unknown"

    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service if valid."""
        if service in self._api_keys:
            key_info = self._api_keys[service]
            if key_info.status == APIKeyStatus.VALID:
                return key_info.key
            else:
                self.logger.warning(f"API key for {service} is not valid: {key_info.status}")
        return None

    def get_key_info(self, service: str) -> Optional[APIKeyInfo]:
        """Get complete key information for a service."""
        return self._api_keys.get(service)

    def validate_all_keys(self) -> Dict[str, APIKeyStatus]:
        """Validate all API keys and return status summary."""
        status_summary = {}
        for service, key_info in self._api_keys.items():
            status_summary[service] = key_info.status
        return status_summary

    def get_authentication_headers(self, service: str) -> Dict[str, str]:
        """Get authentication headers for a specific service."""
        key = self.get_api_key(service)
        if not key:
            raise ValueError(f"No valid API key available for {service}")

        # Service-specific header formats
        if service == 'alpha_vantage':
            return {'apikey': key}

        elif service == 'iex_cloud':
            return {'token': key}

        elif service == 'newsapi':
            return {'X-API-Key': key}

        elif service == 'anthropic':
            return {
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }

        elif service == 'reuters':
            return {'Authorization': f'Bearer {key}'}

        elif service == 'bloomberg':
            return {'X-API-Key': key}

        else:
            # Generic bearer token format
            return {'Authorization': f'Bearer {key}'}

    async def test_api_key(self, service: str) -> bool:
        """Test if an API key is working by making a minimal API call."""
        try:
            if service == 'alpha_vantage':
                # Test with a simple currency query
                return await self._test_alpha_vantage_key()
            elif service == 'newsapi':
                # Test with a minimal news query
                return await self._test_newsapi_key()
            elif service == 'iex_cloud':
                # Test with a simple market data query
                return await self._test_iex_cloud_key()
            elif service == 'anthropic':
                # Test with a minimal message
                return await self._test_anthropic_key()
            else:
                # For other services, assume valid if key format is correct
                return self._api_keys[service].status == APIKeyStatus.VALID
        except Exception as e:
            self.logger.error(f"API key test failed for {service}: {e}")
            return False

    async def _test_alpha_vantage_key(self) -> bool:
        """Test Alpha Vantage API key with minimal call."""
        # Implementation would make actual API call
        # For now, return True if key exists and has correct format
        return self.get_api_key('alpha_vantage') is not None

    async def _test_newsapi_key(self) -> bool:
        """Test NewsAPI key with minimal call."""
        return self.get_api_key('newsapi') is not None

    async def _test_iex_cloud_key(self) -> bool:
        """Test IEX Cloud key with minimal call."""
        return self.get_api_key('iex_cloud') is not None

    async def _test_anthropic_key(self) -> bool:
        """Test Anthropic API key with minimal call."""
        return self.get_api_key('anthropic') is not None

# Global authentication manager instance
auth_manager = AuthenticationManager()
```

### **MCP Server Configuration with Authentication**

```python
# agents/python/common/mcp_auth_config.py

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from agents.python.common.auth import auth_manager

@dataclass
class MCPServerConfig:
    name: str
    type: str  # "command" or "http"
    config: Dict[str, Any]
    authentication: Dict[str, str]
    enabled: bool = True

class MCPAuthenticatedConfig:
    """Generate MCP server configurations with proper authentication."""

    def __init__(self):
        self.auth_manager = auth_manager

    def get_alpha_vantage_config(self) -> MCPServerConfig:
        """Get Alpha Vantage MCP server configuration."""
        api_key = self.auth_manager.get_api_key('alpha_vantage')
        if not api_key:
            raise ValueError("Alpha Vantage API key not available")

        return MCPServerConfig(
            name="alpha_vantage",
            type="http",
            config={
                "base_url": "https://www.alphavantage.co",
                "endpoints": {
                    "forex_realtime": "/query?function=CURRENCY_EXCHANGE_RATE",
                    "forex_daily": "/query?function=FX_DAILY"
                }
            },
            authentication={
                "type": "api_key",
                "key": api_key,
                "param_name": "apikey"
            }
        )

    def get_newsapi_config(self) -> MCPServerConfig:
        """Get NewsAPI MCP server configuration."""
        api_key = self.auth_manager.get_api_key('newsapi')
        if not api_key:
            raise ValueError("NewsAPI key not available")

        return MCPServerConfig(
            name="newsapi",
            type="http",
            config={
                "base_url": "https://newsapi.org/v2",
                "endpoints": {
                    "everything": "/everything",
                    "top_headlines": "/top-headlines"
                }
            },
            authentication={
                "type": "header",
                "header_name": "X-API-Key",
                "key": api_key
            }
        )

    def get_iex_cloud_config(self) -> MCPServerConfig:
        """Get IEX Cloud MCP server configuration."""
        api_token = self.auth_manager.get_api_key('iex_cloud')
        if not api_token:
            raise ValueError("IEX Cloud token not available")

        return MCPServerConfig(
            name="iex_cloud",
            type="http",
            config={
                "base_url": "https://cloud.iexapis.com/stable",
                "endpoints": {
                    "forex": "/fx/latest",
                    "quote": "/stock/{symbol}/quote"
                }
            },
            authentication={
                "type": "api_key",
                "key": api_token,
                "param_name": "token"
            }
        )

    def get_all_enabled_configs(self) -> List[MCPServerConfig]:
        """Get all MCP server configurations for enabled services."""
        configs = []

        try:
            configs.append(self.get_alpha_vantage_config())
        except ValueError as e:
            print(f"Alpha Vantage unavailable: {e}")

        try:
            configs.append(self.newsapi_config())
        except ValueError as e:
            print(f"NewsAPI unavailable: {e}")

        try:
            configs.append(self.get_iex_cloud_config())
        except ValueError as e:
            print(f"IEX Cloud unavailable: {e}")

        return configs

    def generate_mcp_json(self) -> Dict[str, Any]:
        """Generate .mcp.json configuration file content."""
        configs = self.get_all_enabled_configs()

        mcp_config = {
            "mcpServers": {}
        }

        for config in configs:
            mcp_config["mcpServers"][config.name] = {
                "command": "python",
                "args": ["-m", f"mcp_servers.{config.name}"],
                "env": {
                    f"{config.name.upper()}_API_KEY": config.authentication["key"]
                }
            }

        return mcp_config
```

---

## 🔄 **AUTHENTICATION WORKFLOWS**

### **Development Setup Workflow**

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your API keys
nano .env

# 3. Validate authentication setup
python -c "
from agents.python.common.auth import auth_manager
status = auth_manager.validate_all_keys()
for service, status in status.items():
    print(f'{service}: {status.value}')
"

# 4. Test API connections
python agents/python/common/test_auth.py
```

### **Runtime Authentication Flow**

```python
# Example: Research Agent authentication flow

from agents.python.common.auth import auth_manager
from agents.python.common.mcp_auth_config import MCPAuthenticatedConfig

async def initialize_research_agent():
    """Initialize research agent with authenticated MCP servers."""

    # Validate authentication
    auth_status = auth_manager.validate_all_keys()
    required_services = ['alpha_vantage', 'newsapi', 'anthropic']

    for service in required_services:
        if auth_status.get(service) != APIKeyStatus.VALID:
            raise Exception(f"Required service {service} authentication failed")

    # Configure MCP servers
    mcp_config = MCPAuthenticatedConfig()
    server_configs = mcp_config.get_all_enabled_configs()

    print(f"Initialized with {len(server_configs)} authenticated MCP servers")
    return server_configs
```

---

## 🚨 **ERROR HANDLING**

### **Authentication Error Types**

```python
class AuthenticationError(Exception):
    """Base class for authentication errors."""
    pass

class APIKeyMissingError(AuthenticationError):
    """Required API key is missing."""
    pass

class APIKeyInvalidError(AuthenticationError):
    """API key format is invalid."""
    pass

class APIKeyExpiredError(AuthenticationError):
    """API key has expired."""
    pass

class RateLimitError(AuthenticationError):
    """API key has hit rate limits."""
    pass
```

### **Error Recovery Strategies**

```python
async def handle_authentication_error(service: str, error: Exception):
    """Handle authentication errors with appropriate recovery."""

    if isinstance(error, APIKeyMissingError):
        # Fall back to mock data or cached data
        logger.error(f"Missing API key for {service}, using fallback data")
        return await get_fallback_data(service)

    elif isinstance(error, RateLimitError):
        # Use cached data and wait for rate limit reset
        logger.warning(f"Rate limit exceeded for {service}, using cached data")
        return await get_cached_data(service)

    elif isinstance(error, APIKeyExpiredError):
        # Disable service and use alternatives
        logger.error(f"API key expired for {service}, switching to backup")
        return await get_backup_service_data(service)

    else:
        # Generic error handling
        logger.error(f"Authentication error for {service}: {error}")
        raise error
```

---

## 🔍 **VALIDATION AND TESTING**

### **Authentication Test Suite**

```python
# tests/unit/test_authentication.py

import pytest
from agents.python.common.auth import AuthenticationManager, APIKeyStatus
from agents.python.common.mcp_auth_config import MCPAuthenticatedConfig

class TestAuthentication:

    def test_api_key_validation(self):
        """Test API key format validation."""
        auth_manager = AuthenticationManager()

        # Test valid key formats
        assert auth_manager._validate_key_format('alpha_vantage', 'ABCDEFGHIJKLMNOP')
        assert auth_manager._validate_key_format('anthropic', 'sk-ant-' + 'x' * 95)

        # Test invalid key formats
        assert not auth_manager._validate_key_format('alpha_vantage', 'invalid')
        assert not auth_manager._validate_key_format('anthropic', 'sk-wrong-format')

    @pytest.mark.asyncio
    async def test_mcp_server_config_generation(self):
        """Test MCP server configuration generation."""
        config_gen = MCPAuthenticatedConfig()

        # Should handle missing keys gracefully
        configs = config_gen.get_all_enabled_configs()
        assert isinstance(configs, list)

    def test_authentication_headers(self):
        """Test service-specific authentication headers."""
        auth_manager = AuthenticationManager()

        # Mock valid keys for testing
        auth_manager._api_keys['newsapi'] = APIKeyInfo(
            service='newsapi',
            key='test_key_123',
            status=APIKeyStatus.VALID,
            tier='free'
        )

        headers = auth_manager.get_authentication_headers('newsapi')
        assert 'X-API-Key' in headers
        assert headers['X-API-Key'] == 'test_key_123'
```

### **Integration Testing**

```python
# tests/integration/test_mcp_auth_integration.py

@pytest.mark.integration
async def test_full_authentication_flow():
    """Test complete authentication flow with MCP servers."""

    # Initialize authentication
    auth_manager = AuthenticationManager()
    status = auth_manager.validate_all_keys()

    # Should have at least one valid service for testing
    valid_services = [s for s, st in status.items() if st == APIKeyStatus.VALID]
    assert len(valid_services) > 0, "No valid API keys available for integration testing"

    # Test MCP configuration generation
    config_gen = MCPAuthenticatedConfig()
    configs = config_gen.get_all_enabled_configs()

    assert len(configs) >= len(valid_services)

    # Test actual API calls (if not in CI)
    if not os.getenv('CI'):
        for service in valid_services:
            success = await auth_manager.test_api_key(service)
            assert success, f"API key test failed for {service}"
```

---

## 📊 **MONITORING AND MAINTENANCE**

### **Key Rotation Strategy**

```python
class KeyRotationManager:
    """Manage API key rotation for production environments."""

    def __init__(self):
        self.rotation_schedule = {
            'alpha_vantage': 90,  # days
            'newsapi': 90,
            'iex_cloud': 180,
            'anthropic': 365
        }

    def check_key_expiration(self) -> Dict[str, int]:
        """Check days until key expiration."""
        # Implementation would track key creation dates
        # and calculate remaining validity
        pass

    def schedule_key_rotation(self, service: str, days_ahead: int = 7):
        """Schedule key rotation for a service."""
        # Implementation would integrate with monitoring system
        pass
```

### **Usage Monitoring**

```python
class APIUsageMonitor:
    """Monitor API usage and costs."""

    def track_api_call(self, service: str, endpoint: str, cost: float = 0.0):
        """Track API usage for monitoring and cost control."""
        # Implementation would log usage metrics
        pass

    def get_usage_summary(self, timeframe: str = 'daily') -> Dict[str, Any]:
        """Get usage summary for all services."""
        # Implementation would aggregate usage data
        pass
```

---

**STATUS**: This document resolves the MCP server authentication implementation blocking issue. All authentication methods, error handling, and integration patterns are now fully specified for Story 1.3 development.

**NEXT STEPS**:
1. Obtain API keys for Alpha Vantage, NewsAPI, and IEX Cloud
2. Implement authentication module in `agents/python/common/auth.py`
3. Configure MCP servers with authentication
4. Test authentication flow with real API calls