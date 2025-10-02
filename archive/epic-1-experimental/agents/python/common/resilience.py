# Resilience and fallback strategies for MADF agents
# CRITICAL DEVELOPMENT BLOCKER RESOLUTION
# Created: 2025-09-21 | Required for production reliability

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum

class FailureType(Enum):
    """Types of failures that can occur."""
    RATE_LIMIT = "rate_limit"
    API_KEY_INVALID = "api_key_invalid"
    NETWORK_TIMEOUT = "network_timeout"
    SERVER_ERROR = "server_error"
    DATA_FORMAT_ERROR = "data_format_error"
    SERVICE_UNAVAILABLE = "service_unavailable"

@dataclass
class BackoffConfig:
    """Configuration for exponential backoff."""
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    max_retries: int = 3
    jitter: bool = True

@dataclass
class CacheEntry:
    """Cached data entry with metadata."""
    data: Any
    timestamp: datetime
    source: str
    ttl_seconds: int
    confidence_score: float = 1.0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.utcnow() > self.timestamp + timedelta(seconds=self.ttl_seconds)

    def is_stale(self, staleness_threshold_hours: int = 24) -> bool:
        """Check if cache entry is stale but usable."""
        return datetime.utcnow() > self.timestamp + timedelta(hours=staleness_threshold_hours)

    def age_minutes(self) -> float:
        """Get age of cache entry in minutes."""
        return (datetime.utcnow() - self.timestamp).total_seconds() / 60

class DataSourceRegistry:
    """Registry of data sources with priority and capability mapping."""

    def __init__(self):
        self.sources = {
            'forex': [
                {'name': 'alpha_vantage', 'priority': 1, 'capabilities': ['realtime', 'daily', 'asia_g10']},
                {'name': 'iex_cloud', 'priority': 2, 'capabilities': ['realtime', 'backup']},
                {'name': 'cached_data', 'priority': 3, 'capabilities': ['fallback', 'offline']}
            ],
            'news': [
                {'name': 'newsapi', 'priority': 1, 'capabilities': ['financial', 'global', 'recent']},
                {'name': 'reuters', 'priority': 2, 'capabilities': ['validation', 'authoritative']},
                {'name': 'cached_feeds', 'priority': 3, 'capabilities': ['fallback', 'offline']}
            ]
        }

    def get_sources_for_data_type(self, data_type: str, capability: str = None) -> List[Dict[str, Any]]:
        """Get ordered list of sources for a data type, optionally filtered by capability."""
        sources = self.sources.get(data_type, [])
        if capability:
            sources = [s for s in sources if capability in s['capabilities']]
        return sorted(sources, key=lambda x: x['priority'])

class ResilientCache:
    """Cache with multi-tier storage and intelligent retrieval."""

    def __init__(self, cache_dir: Path, default_ttl: int = 300):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.logger = logging.getLogger(__name__)

    def _get_cache_key(self, source: str, request_params: Dict[str, Any]) -> str:
        """Generate cache key from source and parameters."""
        # Sort params for consistent keys
        sorted_params = json.dumps(request_params, sort_keys=True)
        return f"{source}_{hash(sorted_params)}"

    def _get_file_path(self, cache_key: str) -> Path:
        """Get file path for cache key."""
        return self.cache_dir / f"{cache_key}.json"

    async def get(self, source: str, request_params: Dict[str, Any]) -> Optional[CacheEntry]:
        """Get cached entry, checking memory first, then disk."""
        cache_key = self._get_cache_key(source, request_params)

        # Check memory cache first
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if not entry.is_expired():
                self.logger.debug(f"Cache hit (memory): {cache_key}")
                return entry

        # Check disk cache
        file_path = self._get_file_path(cache_key)
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    cache_data = json.load(f)

                entry = CacheEntry(
                    data=cache_data['data'],
                    timestamp=datetime.fromisoformat(cache_data['timestamp']),
                    source=cache_data['source'],
                    ttl_seconds=cache_data['ttl_seconds'],
                    confidence_score=cache_data.get('confidence_score', 1.0)
                )

                if not entry.is_expired():
                    # Promote to memory cache
                    self.memory_cache[cache_key] = entry
                    self.logger.debug(f"Cache hit (disk): {cache_key}")
                    return entry

            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Corrupted cache file {file_path}: {e}")
                file_path.unlink(missing_ok=True)

        return None

    async def get_stale(self, source: str, request_params: Dict[str, Any]) -> Optional[CacheEntry]:
        """Get stale data as fallback (even if expired)."""
        cache_key = self._get_cache_key(source, request_params)

        # Check memory cache
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            self.logger.info(f"Using stale data from memory: {cache_key} (age: {entry.age_minutes():.1f} min)")
            return entry

        # Check disk cache
        file_path = self._get_file_path(cache_key)
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    cache_data = json.load(f)

                entry = CacheEntry(
                    data=cache_data['data'],
                    timestamp=datetime.fromisoformat(cache_data['timestamp']),
                    source=cache_data['source'],
                    ttl_seconds=cache_data['ttl_seconds'],
                    confidence_score=cache_data.get('confidence_score', 0.5)  # Lower confidence for stale data
                )

                self.logger.info(f"Using stale data from disk: {cache_key} (age: {entry.age_minutes():.1f} min)")
                return entry

            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Corrupted stale cache file {file_path}: {e}")

        return None

    async def store(self, source: str, request_params: Dict[str, Any], data: Any,
                   ttl_seconds: int = None, confidence_score: float = 1.0):
        """Store data in both memory and disk cache."""
        cache_key = self._get_cache_key(source, request_params)
        ttl = ttl_seconds or self.default_ttl

        entry = CacheEntry(
            data=data,
            timestamp=datetime.utcnow(),
            source=source,
            ttl_seconds=ttl,
            confidence_score=confidence_score
        )

        # Store in memory
        self.memory_cache[cache_key] = entry

        # Store on disk
        try:
            cache_data = asdict(entry)
            cache_data['timestamp'] = entry.timestamp.isoformat()

            file_path = self._get_file_path(cache_key)
            with open(file_path, 'w') as f:
                json.dump(cache_data, f, indent=2)

            self.logger.debug(f"Cached data: {cache_key}")

        except Exception as e:
            self.logger.error(f"Failed to write cache file {cache_key}: {e}")

    async def cleanup_expired(self):
        """Remove expired entries from memory and disk."""
        # Clean memory cache
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.memory_cache[key]

        # Clean disk cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)

                timestamp = datetime.fromisoformat(cache_data['timestamp'])
                ttl = cache_data['ttl_seconds']

                if datetime.utcnow() > timestamp + timedelta(seconds=ttl):
                    cache_file.unlink()

            except Exception as e:
                self.logger.warning(f"Error cleaning cache file {cache_file}: {e}")

class ResilientDataService:
    """High-level service for resilient data access with multiple fallback strategies."""

    def __init__(self, cache_dir: Path, source_registry: DataSourceRegistry = None):
        self.cache = ResilientCache(cache_dir)
        self.registry = source_registry or DataSourceRegistry()
        self.logger = logging.getLogger(__name__)
        self.circuit_breakers = {}  # Track failing services

    async def get_data(self, data_type: str, request_params: Dict[str, Any],
                      capability: str = None) -> Dict[str, Any]:
        """
        Get data with comprehensive fallback strategy.

        Fallback order:
        1. Try primary sources in priority order
        2. Use fresh cached data if available
        3. Try backup sources
        4. Use stale cached data as last resort
        """
        sources = self.registry.get_sources_for_data_type(data_type, capability)

        # Try each source in priority order
        for source_config in sources:
            source_name = source_config['name']

            # Skip if circuit breaker is open
            if self._is_circuit_breaker_open(source_name):
                self.logger.info(f"Skipping {source_name} - circuit breaker open")
                continue

            try:
                # Check cache first for non-fallback sources
                if 'fallback' not in source_config['capabilities']:
                    cached_entry = await self.cache.get(source_name, request_params)
                    if cached_entry:
                        self.logger.info(f"Using cached data from {source_name}")
                        return self._format_response(cached_entry.data, source_name,
                                                   cached=True, confidence=cached_entry.confidence_score)

                # Try to fetch from source
                if source_name not in ['cached_data', 'cached_feeds']:
                    data = await self._fetch_from_source(source_name, request_params)
                    if data:
                        # Cache successful result
                        await self.cache.store(source_name, request_params, data)
                        self._reset_circuit_breaker(source_name)
                        self.logger.info(f"Successfully fetched from {source_name}")
                        return self._format_response(data, source_name, cached=False, confidence=1.0)

            except Exception as e:
                self.logger.warning(f"Failed to fetch from {source_name}: {e}")
                self._record_failure(source_name)
                continue

        # Last resort: try stale cached data from any source
        for source_config in sources:
            source_name = source_config['name']
            if 'fallback' not in source_config['capabilities']:
                stale_entry = await self.cache.get_stale(source_name, request_params)
                if stale_entry:
                    self.logger.warning(f"Using stale data from {source_name} (age: {stale_entry.age_minutes():.1f} min)")
                    return self._format_response(stale_entry.data, source_name,
                                               cached=True, stale=True, confidence=stale_entry.confidence_score * 0.7)

        # Complete failure
        raise Exception(f"All data sources failed for {data_type}")

    def _format_response(self, data: Any, source: str, cached: bool = False,
                        stale: bool = False, confidence: float = 1.0) -> Dict[str, Any]:
        """Format response with metadata."""
        return {
            'data': data,
            'metadata': {
                'source': source,
                'cached': cached,
                'stale': stale,
                'confidence_score': confidence,
                'timestamp': datetime.utcnow().isoformat(),
                'data_freshness_indicator': 'stale' if stale else ('cached' if cached else 'fresh')
            }
        }

    async def _fetch_from_source(self, source_name: str, request_params: Dict[str, Any]) -> Any:
        """Fetch data from a specific source with retry logic."""
        backoff_config = BackoffConfig()

        for attempt in range(backoff_config.max_retries):
            try:
                # This would call the actual MCP server or API
                # For now, this is a placeholder that would be implemented per source
                return await self._call_mcp_server(source_name, request_params)

            except Exception as e:
                if attempt == backoff_config.max_retries - 1:
                    raise e

                # Calculate backoff delay
                delay = min(
                    backoff_config.initial_delay * (backoff_config.backoff_factor ** attempt),
                    backoff_config.max_delay
                )

                if backoff_config.jitter:
                    delay *= (0.5 + 0.5 * asyncio.get_event_loop().time() % 1)

                self.logger.info(f"Retrying {source_name} in {delay:.1f}s (attempt {attempt + 1})")
                await asyncio.sleep(delay)

    async def _call_mcp_server(self, source_name: str, request_params: Dict[str, Any]) -> Any:
        """Call MCP server - to be implemented per source."""
        # This is a placeholder that would be implemented in the actual agents
        # Each agent would override this method with their specific MCP server calls
        raise NotImplementedError("Subclasses must implement _call_mcp_server")

    def _is_circuit_breaker_open(self, source_name: str) -> bool:
        """Check if circuit breaker is open for a source."""
        if source_name not in self.circuit_breakers:
            return False

        breaker = self.circuit_breakers[source_name]
        if breaker['failure_count'] >= 3:  # Open after 3 failures
            # Check if enough time has passed to try again
            if time.time() - breaker['last_failure'] > 300:  # 5 minutes
                return False
            return True

        return False

    def _record_failure(self, source_name: str):
        """Record a failure for circuit breaker logic."""
        if source_name not in self.circuit_breakers:
            self.circuit_breakers[source_name] = {'failure_count': 0, 'last_failure': 0}

        self.circuit_breakers[source_name]['failure_count'] += 1
        self.circuit_breakers[source_name]['last_failure'] = time.time()

    def _reset_circuit_breaker(self, source_name: str):
        """Reset circuit breaker after successful call."""
        if source_name in self.circuit_breakers:
            self.circuit_breakers[source_name]['failure_count'] = 0

    async def get_service_status(self) -> Dict[str, Any]:
        """Get status of all data sources."""
        status = {}
        for data_type, sources in self.registry.sources.items():
            status[data_type] = {}
            for source in sources:
                source_name = source['name']
                status[data_type][source_name] = {
                    'available': not self._is_circuit_breaker_open(source_name),
                    'failure_count': self.circuit_breakers.get(source_name, {}).get('failure_count', 0),
                    'priority': source['priority'],
                    'capabilities': source['capabilities']
                }

        return status

# Usage examples and factory functions
def create_resilient_service(cache_dir: Path) -> ResilientDataService:
    """Create a configured resilient data service."""
    return ResilientDataService(cache_dir)

async def test_fallback_scenarios():
    """Test various fallback scenarios."""
    service = create_resilient_service(Path("test_cache"))

    scenarios = [
        {"name": "normal_operation", "failure_rate": 0.0},
        {"name": "primary_source_down", "failure_rate": 0.5},
        {"name": "all_sources_failing", "failure_rate": 1.0}
    ]

    for scenario in scenarios:
        print(f"\nTesting scenario: {scenario['name']}")
        try:
            result = await service.get_data('forex', {'pair': 'USD/JPY'})
            print(f"Success: {result['metadata']}")
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_fallback_scenarios())