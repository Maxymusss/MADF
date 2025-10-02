# Mock Bloomberg Service for Development
# Simulates Bloomberg Terminal API responses with realistic data
# Created: 2025-09-21 | For Story 1.1 development without Bloomberg Terminal

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class BloombergSecurityInfo:
    """Bloomberg security information structure."""
    ticker: str
    name: str
    market: str
    currency: str
    sector: Optional[str] = None
    country: Optional[str] = None

@dataclass
class BloombergPriceData:
    """Bloomberg price data structure."""
    security: str
    field: str
    value: Union[float, str, int]
    timestamp: datetime
    source: str = "MOCK_BBG"
    status: str = "OK"

@dataclass
class BloombergNewsItem:
    """Bloomberg news item structure."""
    story_id: str
    headline: str
    summary: str
    datetime_published: datetime
    source: str
    relevance_score: float
    sentiment: str
    securities_mentioned: List[str]
    categories: List[str]

class MockBloombergTerminal:
    """
    Mock Bloomberg Terminal service that simulates BLP API responses.
    Provides realistic data structures matching Bloomberg API format.
    """

    def __init__(self):
        self.session_active = False
        self.daily_request_count = 0
        self.daily_limit = 500000  # Bloomberg daily API limit
        self.real_time_subscriptions = {}
        self.max_real_time_fields = 3500  # Bloomberg real-time limit

        # Initialize mock data
        self._init_mock_securities()
        self._init_mock_rates()

        logger.info("Mock Bloomberg Terminal initialized")

    def _init_mock_securities(self):
        """Initialize mock security definitions."""
        self.securities = {
            # FX Spot Rates
            "USDJPY Curncy": BloombergSecurityInfo("USDJPY Curncy", "USD/JPY Spot Rate", "FX", "JPY"),
            "EURUSD Curncy": BloombergSecurityInfo("EURUSD Curncy", "EUR/USD Spot Rate", "FX", "USD"),
            "GBPUSD Curncy": BloombergSecurityInfo("GBPUSD Curncy", "GBP/USD Spot Rate", "FX", "USD"),
            "AUDUSD Curncy": BloombergSecurityInfo("AUDUSD Curncy", "AUD/USD Spot Rate", "FX", "USD"),
            "USDCHF Curncy": BloombergSecurityInfo("USDCHF Curncy", "USD/CHF Spot Rate", "FX", "CHF"),
            "USDCAD Curncy": BloombergSecurityInfo("USDCAD Curncy", "USD/CAD Spot Rate", "FX", "CAD"),

            # Interest Rates
            "USGG10YR Index": BloombergSecurityInfo("USGG10YR Index", "US Generic Govt 10 Year", "Govt", "USD"),
            "GDBR10 Index": BloombergSecurityInfo("GDBR10 Index", "German 10 Year Government Bond", "Govt", "EUR"),
            "GJGB10 Index": BloombergSecurityInfo("GJGB10 Index", "Japan 10 Year Government Bond", "Govt", "JPY"),
            "GUKG10 Index": BloombergSecurityInfo("GUKG10 Index", "UK 10 Year Government Bond", "Govt", "GBP"),

            # Central Bank Rates
            "FDTR Index": BloombergSecurityInfo("FDTR Index", "Federal Funds Target Rate", "Money Market", "USD"),
            "EURR002W Index": BloombergSecurityInfo("EURR002W Index", "Euro Interbank Offered Rate", "Money Market", "EUR"),
            "JYDR1T Curncy": BloombergSecurityInfo("JYDR1T Curncy", "Japan Discount Rate", "Money Market", "JPY"),
        }

    def _init_mock_rates(self):
        """Initialize mock interest rate data."""
        self.base_rates = {
            "USDJPY Curncy": 150.25,
            "EURUSD Curncy": 1.0821,
            "GBPUSD Curncy": 1.2634,
            "AUDUSD Curncy": 0.6545,
            "USDCHF Curncy": 0.8879,
            "USDCAD Curncy": 1.3651,
            "USGG10YR Index": 4.45,
            "GDBR10 Index": 2.87,
            "GJGB10 Index": 0.75,
            "GUKG10 Index": 4.12,
            "FDTR Index": 5.50,
            "EURR002W Index": 3.75,
            "JYDR1T Curncy": 0.25,
        }

    async def start_session(self, host: str = "localhost", port: int = 8194) -> bool:
        """
        Simulate starting Bloomberg Terminal session.
        In real implementation, this would connect to localhost:8194
        """
        await asyncio.sleep(0.1)  # Simulate connection time
        self.session_active = True
        logger.info(f"Mock Bloomberg session started (simulating {host}:{port})")
        return True

    async def stop_session(self):
        """Stop Bloomberg Terminal session."""
        self.session_active = False
        self.real_time_subscriptions.clear()
        logger.info("Mock Bloomberg session stopped")

    def _check_session(self):
        """Check if session is active."""
        if not self.session_active:
            raise ConnectionError("Bloomberg session not active. Call start_session() first.")

    def _check_daily_limit(self, num_requests: int = 1):
        """Check and update daily API usage."""
        if self.daily_request_count + num_requests > self.daily_limit:
            raise Exception(f"Daily API limit exceeded: {self.daily_request_count}/{self.daily_limit}")
        self.daily_request_count += num_requests

    def _generate_realistic_price(self, security: str, field: str) -> float:
        """Generate realistic price data with small random variations."""
        base_value = self.base_rates.get(security, 100.0)

        # Add small random variation (±0.5%)
        variation = random.uniform(-0.005, 0.005)
        return round(base_value * (1 + variation), 4)

    async def reference_data_request(self, securities: List[str], fields: List[str]) -> List[BloombergPriceData]:
        """
        Simulate Bloomberg reference data request.
        Equivalent to bdp() function in Bloomberg Excel/API.
        """
        self._check_session()

        # Calculate API hits (securities × fields)
        num_hits = len(securities) * len(fields)
        self._check_daily_limit(num_hits)

        results = []
        current_time = datetime.utcnow()

        for security in securities:
            if security not in self.securities:
                # Return error for unknown security
                for field in fields:
                    results.append(BloombergPriceData(
                        security=security,
                        field=field,
                        value="N.A.",
                        timestamp=current_time,
                        status="UNKNOWN_SECURITY"
                    ))
                continue

            for field in fields:
                if field in ["PX_LAST", "LAST_PRICE"]:
                    value = self._generate_realistic_price(security, field)
                elif field in ["PX_BID", "BID"]:
                    last_price = self._generate_realistic_price(security, "PX_LAST")
                    value = round(last_price - 0.002, 4)  # Bid slightly lower
                elif field in ["PX_ASK", "ASK"]:
                    last_price = self._generate_realistic_price(security, "PX_LAST")
                    value = round(last_price + 0.002, 4)  # Ask slightly higher
                elif field in ["CHG_PCT_1D", "DAY_CHG_PCT"]:
                    value = round(random.uniform(-2.5, 2.5), 2)  # Daily change %
                elif field in ["VOLUME", "PX_VOLUME"]:
                    value = random.randint(10000, 1000000)
                elif field in ["SECURITY_NAME", "NAME"]:
                    value = self.securities[security].name
                elif field in ["CRNCY", "CURRENCY"]:
                    value = self.securities[security].currency
                elif field in ["MARKET_SECTOR_DES"]:
                    value = self.securities[security].market
                else:
                    value = "N.A."  # Field not supported in mock

                results.append(BloombergPriceData(
                    security=security,
                    field=field,
                    value=value,
                    timestamp=current_time,
                    status="OK"
                ))

        # Simulate API response time
        await asyncio.sleep(random.uniform(0.1, 0.5))

        logger.debug(f"Reference data request completed: {len(securities)} securities, {len(fields)} fields")
        return results

    async def historical_data_request(self, security: str, fields: List[str],
                                    start_date: datetime, end_date: datetime) -> List[BloombergPriceData]:
        """
        Simulate Bloomberg historical data request.
        Equivalent to bdh() function in Bloomberg Excel/API.
        """
        self._check_session()

        # Calculate number of days and API hits
        date_range = (end_date - start_date).days + 1
        num_hits = date_range * len(fields)
        self._check_daily_limit(num_hits)

        if security not in self.securities:
            raise ValueError(f"Unknown security: {security}")

        results = []
        current_date = start_date

        while current_date <= end_date:
            # Skip weekends for financial data
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                for field in fields:
                    if field in ["PX_LAST", "LAST_PRICE"]:
                        value = self._generate_realistic_price(security, field)
                    elif field in ["PX_HIGH", "HIGH"]:
                        last_price = self._generate_realistic_price(security, "PX_LAST")
                        value = round(last_price * random.uniform(1.001, 1.01), 4)
                    elif field in ["PX_LOW", "LOW"]:
                        last_price = self._generate_realistic_price(security, "PX_LAST")
                        value = round(last_price * random.uniform(0.99, 0.999), 4)
                    elif field in ["VOLUME", "PX_VOLUME"]:
                        value = random.randint(50000, 2000000)
                    else:
                        value = "N.A."

                    results.append(BloombergPriceData(
                        security=security,
                        field=field,
                        value=value,
                        timestamp=current_date,
                        status="OK"
                    ))

            current_date += timedelta(days=1)

        # Simulate API response time based on data volume
        await asyncio.sleep(random.uniform(0.5, 2.0))

        logger.debug(f"Historical data request completed: {security}, {len(fields)} fields, {date_range} days")
        return results

    async def get_news(self, query: str = None, start_date: datetime = None,
                      end_date: datetime = None, max_results: int = 50) -> List[BloombergNewsItem]:
        """
        Simulate Bloomberg news search.
        """
        self._check_session()
        self._check_daily_limit(max_results)  # Each news item counts as 1 hit

        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.utcnow()

        # Generate mock news items
        news_items = []

        mock_headlines = [
            "Federal Reserve Signals Potential Policy Shift as Inflation Moderates",
            "European Central Bank Maintains Cautious Stance Amid Economic Uncertainty",
            "Bank of Japan Keeps Ultra-Loose Monetary Policy Despite Global Tightening",
            "USD/JPY Reaches Fresh Multi-Year Highs on Rate Differential Widening",
            "EUR/USD Struggles Near Parity as ECB Dovish Signals Persist",
            "Australian Dollar Weakens on RBA Rate Cut Speculation",
            "Swiss Franc Strengthens as Safe Haven Demand Increases",
            "Canadian Dollar Volatile Following Bank of Canada Decision",
            "G10 Currency Volatility Surges Amid Central Bank Divergence",
            "Asian FX Markets Show Mixed Performance on Trade Data"
        ]

        num_items = min(max_results, len(mock_headlines))

        for i in range(num_items):
            story_time = start_date + timedelta(
                hours=random.randint(0, int((end_date - start_date).total_seconds() // 3600))
            )

            headline = mock_headlines[i % len(mock_headlines)]

            # Determine relevant securities based on headline
            relevant_securities = []
            if "Fed" in headline or "USD" in headline:
                relevant_securities.extend(["USDJPY Curncy", "EURUSD Curncy", "FDTR Index"])
            if "ECB" in headline or "EUR" in headline:
                relevant_securities.extend(["EURUSD Curncy", "EURR002W Index"])
            if "BoJ" in headline or "JPY" in headline:
                relevant_securities.extend(["USDJPY Curncy", "JYDR1T Curncy"])

            news_items.append(BloombergNewsItem(
                story_id=f"BBG_NEWS_{story_time.strftime('%Y%m%d')}_{i:03d}",
                headline=headline,
                summary=f"Summary of {headline.lower()} with market implications and analyst commentary.",
                datetime_published=story_time,
                source="Bloomberg News",
                relevance_score=random.uniform(0.6, 0.95),
                sentiment=random.choice(["positive", "negative", "neutral"]),
                securities_mentioned=relevant_securities[:3],  # Limit to top 3
                categories=["Central Banks", "Foreign Exchange", "Interest Rates"]
            ))

        # Simulate API response time
        await asyncio.sleep(random.uniform(0.3, 1.0))

        logger.debug(f"News search completed: {len(news_items)} items found")
        return news_items

    async def subscribe_real_time(self, securities: List[str], fields: List[str]) -> str:
        """
        Simulate real-time data subscription.
        Returns subscription ID.
        """
        self._check_session()

        # Check real-time field limit
        total_fields = sum(len(fields) for securities in self.real_time_subscriptions.values())
        new_fields = len(securities) * len(fields)

        if total_fields + new_fields > self.max_real_time_fields:
            raise Exception(f"Real-time field limit exceeded. Current: {total_fields}, Limit: {self.max_real_time_fields}")

        subscription_id = f"sub_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"

        self.real_time_subscriptions[subscription_id] = {
            "securities": securities,
            "fields": fields,
            "start_time": datetime.utcnow()
        }

        logger.info(f"Real-time subscription created: {subscription_id}")
        return subscription_id

    async def get_real_time_data(self, subscription_id: str) -> List[BloombergPriceData]:
        """
        Get current real-time data for a subscription.
        """
        self._check_session()

        if subscription_id not in self.real_time_subscriptions:
            raise ValueError(f"Unknown subscription: {subscription_id}")

        subscription = self.real_time_subscriptions[subscription_id]
        results = []
        current_time = datetime.utcnow()

        for security in subscription["securities"]:
            for field in subscription["fields"]:
                if field in ["PX_LAST", "LAST_PRICE"]:
                    value = self._generate_realistic_price(security, field)
                elif field in ["PX_BID", "BID"]:
                    last_price = self._generate_realistic_price(security, "PX_LAST")
                    value = round(last_price - random.uniform(0.001, 0.005), 4)
                elif field in ["PX_ASK", "ASK"]:
                    last_price = self._generate_realistic_price(security, "PX_LAST")
                    value = round(last_price + random.uniform(0.001, 0.005), 4)
                else:
                    value = self._generate_realistic_price(security, field)

                results.append(BloombergPriceData(
                    security=security,
                    field=field,
                    value=value,
                    timestamp=current_time,
                    status="OK",
                    source="REAL_TIME"
                ))

        return results

    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        return {
            "session_active": self.session_active,
            "daily_requests_used": self.daily_request_count,
            "daily_requests_remaining": self.daily_limit - self.daily_request_count,
            "real_time_subscriptions": len(self.real_time_subscriptions),
            "real_time_fields_used": sum(
                len(sub["securities"]) * len(sub["fields"])
                for sub in self.real_time_subscriptions.values()
            ),
            "real_time_fields_remaining": self.max_real_time_fields - sum(
                len(sub["securities"]) * len(sub["fields"])
                for sub in self.real_time_subscriptions.values()
            )
        }

# Convenience functions
async def create_mock_bloomberg_session() -> MockBloombergTerminal:
    """Create and start a mock Bloomberg session."""
    terminal = MockBloombergTerminal()
    await terminal.start_session()
    return terminal

# Export main classes
__all__ = [
    "MockBloombergTerminal",
    "BloombergSecurityInfo",
    "BloombergPriceData",
    "BloombergNewsItem",
    "create_mock_bloomberg_session"
]