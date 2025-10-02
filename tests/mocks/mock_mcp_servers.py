# Mock MCP servers for offline development and testing
# CRITICAL DEVELOPMENT BLOCKER RESOLUTION
# Created: 2025-09-21 | Required for Story 1.3 development

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from unittest.mock import AsyncMock
from pathlib import Path
import random

from tests.fixtures.sample_data import TestDataGenerator

class MockAlphaVantageServer:
    """Mock Alpha Vantage MCP server for forex and market data."""

    def __init__(self, use_realistic_delays: bool = True):
        self.use_realistic_delays = use_realistic_delays
        self.call_count = 0
        self.rate_limit_calls_per_minute = 5
        self.call_times = []

    async def _check_rate_limit(self):
        """Simulate rate limiting like real Alpha Vantage API."""
        now = datetime.utcnow()
        # Remove calls older than 1 minute
        self.call_times = [t for t in self.call_times if (now - t).seconds < 60]

        if len(self.call_times) >= self.rate_limit_calls_per_minute:
            raise Exception("Rate limit exceeded: 5 calls per minute")

        self.call_times.append(now)
        self.call_count += 1

        if self.use_realistic_delays:
            # Simulate API response time
            await asyncio.sleep(random.uniform(0.5, 2.0))

    async def get_forex_realtime(self, from_symbol: str, to_symbol: str) -> Dict[str, Any]:
        """Mock forex realtime data endpoint."""
        await self._check_rate_limit()

        forex_data = TestDataGenerator.get_asia_g10_forex_data()
        pair_key = f"{from_symbol}/{to_symbol}"

        if pair_key in forex_data:
            result = forex_data[pair_key].copy()
            # Add some random variation to make it realistic
            base_price = result['price']
            variation = random.uniform(-0.002, 0.002)  # ±0.2% variation
            result['price'] = round(base_price * (1 + variation), 5)
            result['timestamp'] = datetime.utcnow().isoformat()
            result['mock_call_id'] = self.call_count
            return {
                "Realtime Currency Exchange Rate": {
                    "1. From_Currency Code": from_symbol,
                    "2. From_Currency Name": self._get_currency_name(from_symbol),
                    "3. To_Currency Code": to_symbol,
                    "4. To_Currency Name": self._get_currency_name(to_symbol),
                    "5. Exchange Rate": str(result['price']),
                    "6. Last Refreshed": result['timestamp'],
                    "7. Time Zone": "UTC",
                    "8. Bid Price": str(result['bid']),
                    "9. Ask Price": str(result['ask'])
                }
            }
        else:
            raise Exception(f"Currency pair {pair_key} not supported in mock data")

    async def get_forex_daily(self, from_symbol: str, to_symbol: str, outputsize: str = "compact") -> Dict[str, Any]:
        """Mock forex daily data endpoint."""
        await self._check_rate_limit()

        # Generate daily data for the past week
        daily_data = {}
        base_date = datetime.utcnow().date()
        forex_data = TestDataGenerator.get_asia_g10_forex_data()
        pair_key = f"{from_symbol}/{to_symbol}"

        if pair_key not in forex_data:
            raise Exception(f"Currency pair {pair_key} not supported")

        base_price = forex_data[pair_key]['price']

        for i in range(7):  # Last 7 days
            date = base_date - timedelta(days=i)
            daily_variation = random.uniform(-0.01, 0.01)  # ±1% daily variation
            price = base_price * (1 + daily_variation)

            daily_data[date.isoformat()] = {
                "1. open": str(round(price * 0.999, 5)),
                "2. high": str(round(price * 1.005, 5)),
                "3. low": str(round(price * 0.995, 5)),
                "4. close": str(round(price, 5))
            }

        return {
            "Meta Data": {
                "1. Information": f"Forex Daily Time Series ({from_symbol}/{to_symbol})",
                "2. From Symbol": from_symbol,
                "3. To Symbol": to_symbol,
                "4. Output Size": outputsize,
                "5. Last Refreshed": datetime.utcnow().isoformat(),
                "6. Time Zone": "UTC"
            },
            "Time Series FX (Daily)": daily_data
        }

    def _get_currency_name(self, code: str) -> str:
        """Get full currency name from code."""
        names = {
            "USD": "United States Dollar",
            "EUR": "Euro",
            "JPY": "Japanese Yen",
            "GBP": "British Pound Sterling",
            "CHF": "Swiss Franc",
            "CAD": "Canadian Dollar",
            "AUD": "Australian Dollar"
        }
        return names.get(code, f"Currency {code}")

class MockNewsAPIServer:
    """Mock NewsAPI server for financial news."""

    def __init__(self, use_realistic_delays: bool = True):
        self.use_realistic_delays = use_realistic_delays
        self.call_count = 0
        self.daily_limit = 33  # Conservative limit for free tier
        self.daily_calls = []

    async def _check_rate_limit(self):
        """Simulate NewsAPI rate limiting."""
        now = datetime.utcnow()
        today = now.date()

        # Remove calls from previous days
        self.daily_calls = [t for t in self.daily_calls if t.date() == today]

        if len(self.daily_calls) >= self.daily_limit:
            raise Exception("Daily request limit exceeded: 1000 requests per month (33 per day)")

        self.daily_calls.append(now)
        self.call_count += 1

        if self.use_realistic_delays:
            await asyncio.sleep(random.uniform(0.3, 1.5))

    async def everything(self, q: str, from_date: str = None, to_date: str = None,
                        language: str = "en", sort_by: str = "relevancy") -> Dict[str, Any]:
        """Mock news everything endpoint."""
        await self._check_rate_limit()

        news_data = TestDataGenerator.get_financial_news_data()

        # Filter articles based on query
        filtered_articles = []
        query_lower = q.lower()

        for article in news_data['articles']:
            # Simple keyword matching
            title_match = any(keyword in article['title'].lower() for keyword in query_lower.split())
            desc_match = any(keyword in article['description'].lower() for keyword in query_lower.split())

            if title_match or desc_match:
                # Add mock-specific fields
                article_copy = article.copy()
                article_copy['urlToImage'] = f"https://example.com/image_{random.randint(1000, 9999)}.jpg"
                article_copy['mock_call_id'] = self.call_count
                filtered_articles.append(article_copy)

        # Apply date filtering if specified
        if from_date or to_date:
            filtered_by_date = []
            for article in filtered_articles:
                pub_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))

                include = True
                if from_date:
                    from_dt = datetime.fromisoformat(from_date + 'T00:00:00+00:00')
                    if pub_date < from_dt:
                        include = False

                if to_date and include:
                    to_dt = datetime.fromisoformat(to_date + 'T23:59:59+00:00')
                    if pub_date > to_dt:
                        include = False

                if include:
                    filtered_by_date.append(article)

            filtered_articles = filtered_by_date

        return {
            "status": "ok",
            "totalResults": len(filtered_articles),
            "articles": filtered_articles[:20]  # NewsAPI returns max 20 for free tier
        }

class MockIEXCloudServer:
    """Mock IEX Cloud server for backup forex data."""

    def __init__(self, use_realistic_delays: bool = True):
        self.use_realistic_delays = use_realistic_delays
        self.call_count = 0
        self.monthly_limit = 500000  # Very generous for testing
        self.monthly_calls = []

    async def _check_rate_limit(self):
        """Simulate IEX Cloud rate limiting."""
        now = datetime.utcnow()
        current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Remove calls from previous months
        self.monthly_calls = [t for t in self.monthly_calls if t >= current_month]

        if len(self.monthly_calls) >= self.monthly_limit:
            raise Exception("Monthly message limit exceeded: 500,000 messages per month")

        self.monthly_calls.append(now)
        self.call_count += 1

        if self.use_realistic_delays:
            await asyncio.sleep(random.uniform(0.2, 1.0))

    async def get_fx_rate(self, symbols: str) -> Dict[str, Any]:
        """Mock forex rate endpoint."""
        await self._check_rate_limit()

        forex_data = TestDataGenerator.get_asia_g10_forex_data()
        results = []

        for symbol in symbols.split(','):
            symbol = symbol.strip().upper()
            if symbol in forex_data:
                data = forex_data[symbol]
                results.append({
                    "symbol": symbol,
                    "rate": data['price'],
                    "timestamp": data['timestamp'],
                    "isDuplicate": False
                })

        return results

class MockReutersServer:
    """Mock Reuters server for validation data."""

    def __init__(self, use_realistic_delays: bool = True):
        self.use_realistic_delays = use_realistic_delays
        self.call_count = 0
        self.rate_limit_per_minute = 6
        self.call_times = []

    async def _check_rate_limit(self):
        """Simulate Reuters rate limiting."""
        now = datetime.utcnow()
        self.call_times = [t for t in self.call_times if (now - t).seconds < 60]

        if len(self.call_times) >= self.rate_limit_per_minute:
            raise Exception("Rate limit exceeded: 6 requests per minute")

        self.call_times.append(now)
        self.call_count += 1

        if self.use_realistic_delays:
            await asyncio.sleep(random.uniform(1.0, 3.0))  # Reuters is slower

    async def search_news(self, query: str, from_date: str = None, to_date: str = None) -> Dict[str, Any]:
        """Mock Reuters news search."""
        await self._check_rate_limit()

        # Use subset of news data with Reuters branding
        news_data = TestDataGenerator.get_financial_news_data()
        reuters_articles = [
            article for article in news_data['articles']
            if 'reuters' in article['source']['name'].lower()
        ]

        # Add Reuters-specific fields
        for article in reuters_articles:
            article['wire_service'] = 'Reuters'
            article['story_id'] = f"nL{random.randint(1000000, 9999999)}"
            article['priority'] = random.choice(['urgent', 'normal', 'flash'])
            article['mock_call_id'] = self.call_count

        return {
            "status": "success",
            "total_found": len(reuters_articles),
            "articles": reuters_articles,
            "query_time_ms": random.randint(200, 800)
        }

class MockMCPServerRegistry:
    """Registry for all mock MCP servers."""

    def __init__(self, realistic_delays: bool = True):
        self.servers = {
            'alpha_vantage': MockAlphaVantageServer(realistic_delays),
            'newsapi': MockNewsAPIServer(realistic_delays),
            'iex_cloud': MockIEXCloudServer(realistic_delays),
            'reuters': MockReutersServer(realistic_delays)
        }
        self.failure_rate = 0.0  # 0% failure rate by default

    def set_failure_rate(self, rate: float):
        """Set global failure rate for testing error handling."""
        self.failure_rate = max(0.0, min(1.0, rate))

    async def call_server(self, server_name: str, method: str, **kwargs):
        """Route calls to appropriate mock server with optional failure simulation."""
        if random.random() < self.failure_rate:
            raise Exception(f"Mock network failure for {server_name}")

        if server_name not in self.servers:
            raise Exception(f"Unknown server: {server_name}")

        server = self.servers[server_name]
        if not hasattr(server, method):
            raise Exception(f"Server {server_name} has no method {method}")

        method_func = getattr(server, method)
        return await method_func(**kwargs)

    def get_call_statistics(self) -> Dict[str, Any]:
        """Get statistics about mock server usage."""
        stats = {}
        for name, server in self.servers.items():
            stats[name] = {
                'total_calls': server.call_count,
                'server_type': type(server).__name__
            }
        return stats

    def reset_all_counters(self):
        """Reset call counters for all servers."""
        for server in self.servers.values():
            server.call_count = 0
            if hasattr(server, 'call_times'):
                server.call_times = []
            if hasattr(server, 'daily_calls'):
                server.daily_calls = []
            if hasattr(server, 'monthly_calls'):
                server.monthly_calls = []

# Global registry instance
mock_registry = MockMCPServerRegistry()

# Convenience functions for testing
async def create_test_mcp_environment(test_config: Dict[str, Any] = None):
    """Create a complete mock MCP environment for testing."""
    config = test_config or {}

    registry = MockMCPServerRegistry(
        realistic_delays=config.get('realistic_delays', False)  # Faster for tests
    )

    if config.get('failure_rate'):
        registry.set_failure_rate(config['failure_rate'])

    return registry

def get_mock_server_config() -> Dict[str, Any]:
    """Get mock server configuration for use in agent initialization."""
    return {
        'alpha_vantage': {
            'type': 'mock',
            'class': 'MockAlphaVantageServer',
            'endpoints': ['get_forex_realtime', 'get_forex_daily']
        },
        'newsapi': {
            'type': 'mock',
            'class': 'MockNewsAPIServer',
            'endpoints': ['everything']
        },
        'iex_cloud': {
            'type': 'mock',
            'class': 'MockIEXCloudServer',
            'endpoints': ['get_fx_rate']
        },
        'reuters': {
            'type': 'mock',
            'class': 'MockReutersServer',
            'endpoints': ['search_news']
        }
    }