# Bloomberg API Service - Real and Mock Integration
# Handles both real Bloomberg Terminal API and mock service for development
# Created: 2025-09-21 | Story 1.1 Implementation

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from .models import BloombergDataPoint, BloombergNewsItem, BloombergSecurity
from .mock_bloomberg import MockBloombergTerminal, create_mock_bloomberg_session

logger = logging.getLogger(__name__)

class BloombergConnectionType(Enum):
    MOCK = "mock"
    TERMINAL_API = "terminal_api"  # Desktop API (localhost:8194)
    SERVER_API = "server_api"     # SAPI

@dataclass
class BloombergConfig:
    """Bloomberg service configuration."""
    connection_type: BloombergConnectionType
    host: str = "localhost"
    port: int = 8194
    timeout_seconds: int = 30
    max_daily_requests: int = 500000
    max_real_time_fields: int = 3500
    enable_rate_limiting: bool = True
    mock_realistic_delays: bool = True

class BloombergAPIError(Exception):
    """Bloomberg API specific errors."""
    pass

class BloombergRateLimitError(BloombergAPIError):
    """Bloomberg rate limit exceeded."""
    pass

class BloombergConnectionError(BloombergAPIError):
    """Bloomberg connection failed."""
    pass

class BloombergService:
    """
    Unified Bloomberg service that can use either real Bloomberg Terminal API
    or mock service for development. Automatically detects availability.
    """

    def __init__(self, config: Optional[BloombergConfig] = None):
        self.config = config or self._create_default_config()
        self.connection_type = self.config.connection_type
        self.session = None
        self._daily_request_count = 0
        self._session_start_time = None

        logger.info(f"Bloomberg service initialized with {self.connection_type.value} connection")

    def _create_default_config(self) -> BloombergConfig:
        """Create default configuration based on environment."""
        # Check environment variables for configuration
        use_bloomberg = os.getenv('USE_BLOOMBERG', 'false').lower() == 'true'
        bloomberg_host = os.getenv('BLOOMBERG_HOST', 'localhost')
        bloomberg_port = int(os.getenv('BLOOMBERG_PORT', '8194'))

        if use_bloomberg:
            # Try to detect if Bloomberg Terminal is available
            if self._is_bloomberg_terminal_available():
                connection_type = BloombergConnectionType.TERMINAL_API
                logger.info("Bloomberg Terminal detected, using Terminal API")
            else:
                logger.warning("Bloomberg Terminal not available, falling back to mock")
                connection_type = BloombergConnectionType.MOCK
        else:
            connection_type = BloombergConnectionType.MOCK
            logger.info("Using mock Bloomberg service for development")

        return BloombergConfig(
            connection_type=connection_type,
            host=bloomberg_host,
            port=bloomberg_port,
            mock_realistic_delays=os.getenv('MOCK_REALISTIC_DELAYS', 'true').lower() == 'true'
        )

    def _is_bloomberg_terminal_available(self) -> bool:
        """Check if Bloomberg Terminal is available on localhost:8194."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.config.host, self.config.port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Bloomberg Terminal availability check failed: {e}")
            return False

    async def start_session(self) -> bool:
        """Start Bloomberg session based on connection type."""
        try:
            if self.connection_type == BloombergConnectionType.MOCK:
                self.session = await create_mock_bloomberg_session()
            elif self.connection_type == BloombergConnectionType.TERMINAL_API:
                self.session = await self._start_real_bloomberg_session()
            else:
                raise BloombergAPIError(f"Unsupported connection type: {self.connection_type}")

            self._session_start_time = datetime.utcnow()
            logger.info(f"Bloomberg session started successfully ({self.connection_type.value})")
            return True

        except Exception as e:
            logger.error(f"Failed to start Bloomberg session: {e}")
            # Fallback to mock if real Bloomberg fails
            if self.connection_type != BloombergConnectionType.MOCK:
                logger.info("Falling back to mock Bloomberg service")
                self.connection_type = BloombergConnectionType.MOCK
                self.session = await create_mock_bloomberg_session()
                self._session_start_time = datetime.utcnow()
                return True
            raise BloombergConnectionError(f"Failed to start Bloomberg session: {e}")

    async def _start_real_bloomberg_session(self):
        """Start real Bloomberg Terminal API session."""
        try:
            # Import blpapi only when needed to avoid dependency issues in mock mode
            import blpapi

            # Create session options
            session_options = blpapi.SessionOptions()
            session_options.setServerHost(self.config.host)
            session_options.setServerPort(self.config.port)

            # Create and start session
            session = blpapi.Session(session_options)
            if not session.start():
                raise BloombergConnectionError("Failed to start Bloomberg session")

            # Open reference data service
            if not session.openService("//blp/refdata"):
                raise BloombergConnectionError("Failed to open Bloomberg reference data service")

            logger.info(f"Bloomberg Terminal API session started on {self.config.host}:{self.config.port}")
            return session

        except ImportError:
            raise BloombergAPIError("blpapi package not installed. Install with: pip install blpapi")
        except Exception as e:
            raise BloombergConnectionError(f"Bloomberg Terminal connection failed: {e}")

    async def stop_session(self):
        """Stop Bloomberg session."""
        if self.session:
            if self.connection_type == BloombergConnectionType.MOCK:
                await self.session.stop_session()
            elif hasattr(self.session, 'stop'):
                self.session.stop()

            self.session = None
            self._session_start_time = None
            logger.info("Bloomberg session stopped")

    def _check_session(self):
        """Verify session is active."""
        if not self.session:
            raise BloombergConnectionError("Bloomberg session not active. Call start_session() first.")

    def _check_rate_limits(self, num_requests: int = 1):
        """Check Bloomberg API rate limits."""
        if not self.config.enable_rate_limiting:
            return

        if self._daily_request_count + num_requests > self.config.max_daily_requests:
            raise BloombergRateLimitError(
                f"Daily API limit exceeded: {self._daily_request_count}/{self.config.max_daily_requests}"
            )

        self._daily_request_count += num_requests

    async def get_reference_data(self, securities: List[str], fields: List[str]) -> List[BloombergDataPoint]:
        """
        Get Bloomberg reference data for securities and fields.

        Args:
            securities: List of Bloomberg tickers (e.g., ['USDJPY Curncy', 'EURUSD Curncy'])
            fields: List of Bloomberg fields (e.g., ['PX_LAST', 'PX_BID', 'PX_ASK'])

        Returns:
            List of BloombergDataPoint objects
        """
        self._check_session()
        num_requests = len(securities) * len(fields)
        self._check_rate_limits(num_requests)

        try:
            if self.connection_type == BloombergConnectionType.MOCK:
                return await self.session.reference_data_request(securities, fields)
            else:
                return await self._get_real_reference_data(securities, fields)

        except Exception as e:
            logger.error(f"Reference data request failed: {e}")
            raise BloombergAPIError(f"Reference data request failed: {e}")

    async def _get_real_reference_data(self, securities: List[str], fields: List[str]) -> List[BloombergDataPoint]:
        """Get reference data from real Bloomberg Terminal API."""
        try:
            import blpapi

            # Create request
            ref_data_service = self.session.getService("//blp/refdata")
            request = ref_data_service.createRequest("ReferenceDataRequest")

            # Add securities
            for security in securities:
                request.getElement("securities").appendValue(security)

            # Add fields
            for field in fields:
                request.getElement("fields").appendValue(field)

            # Send request
            logger.debug(f"Sending Bloomberg reference data request: {len(securities)} securities, {len(fields)} fields")
            correlation_id = blpapi.CorrelationId()
            self.session.sendRequest(request, correlation_id)

            # Process response
            results = []
            while True:
                event = self.session.nextEvent(self.config.timeout_seconds * 1000)

                if event.eventType() == blpapi.Event.RESPONSE:
                    for message in event:
                        if message.messageType() == "ReferenceDataResponse":
                            security_data = message.getElement("securityData")

                            for i in range(security_data.numValues()):
                                security_element = security_data.getValue(i)
                                security_name = security_element.getElement("security").getValue()
                                field_data = security_element.getElement("fieldData")

                                for field in fields:
                                    try:
                                        if field_data.hasElement(field):
                                            value = field_data.getElement(field).getValue()
                                            results.append(BloombergDataPoint(
                                                security=security_name,
                                                field=field,
                                                value=value,
                                                timestamp=datetime.utcnow(),
                                                source="BBG_TERMINAL"
                                            ))
                                    except Exception as field_error:
                                        logger.warning(f"Error getting field {field} for {security_name}: {field_error}")
                    break

                elif event.eventType() == blpapi.Event.TIMEOUT:
                    raise BloombergAPIError("Bloomberg request timeout")

            logger.debug(f"Bloomberg reference data request completed: {len(results)} data points")
            return results

        except Exception as e:
            logger.error(f"Real Bloomberg reference data request failed: {e}")
            raise BloombergAPIError(f"Real Bloomberg API error: {e}")

    async def get_historical_data(self, security: str, fields: List[str],
                                start_date: datetime, end_date: datetime) -> List[BloombergDataPoint]:
        """
        Get Bloomberg historical data.

        Args:
            security: Bloomberg ticker
            fields: List of Bloomberg fields
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            List of BloombergDataPoint objects
        """
        self._check_session()

        # Calculate API usage
        days = (end_date - start_date).days + 1
        num_requests = days * len(fields)
        self._check_rate_limits(num_requests)

        try:
            if self.connection_type == BloombergConnectionType.MOCK:
                return await self.session.historical_data_request(security, fields, start_date, end_date)
            else:
                return await self._get_real_historical_data(security, fields, start_date, end_date)

        except Exception as e:
            logger.error(f"Historical data request failed: {e}")
            raise BloombergAPIError(f"Historical data request failed: {e}")

    async def _get_real_historical_data(self, security: str, fields: List[str],
                                      start_date: datetime, end_date: datetime) -> List[BloombergDataPoint]:
        """Get historical data from real Bloomberg Terminal API."""
        # Implementation would be similar to reference data but using HistoricalDataRequest
        # This is a placeholder - full implementation would require detailed blpapi handling
        raise NotImplementedError("Real Bloomberg historical data not implemented in MVP")

    async def get_news(self, query: str = None, start_date: datetime = None,
                      end_date: datetime = None, max_results: int = 50) -> List[BloombergNewsItem]:
        """
        Get Bloomberg news items.

        Args:
            query: Search query
            start_date: Start date for news search
            end_date: End date for news search
            max_results: Maximum number of results

        Returns:
            List of BloombergNewsItem objects
        """
        self._check_session()
        self._check_rate_limits(max_results)

        try:
            if self.connection_type == BloombergConnectionType.MOCK:
                return await self.session.get_news(query, start_date, end_date, max_results)
            else:
                return await self._get_real_news(query, start_date, end_date, max_results)

        except Exception as e:
            logger.error(f"News request failed: {e}")
            raise BloombergAPIError(f"News request failed: {e}")

    async def _get_real_news(self, query: str, start_date: datetime,
                           end_date: datetime, max_results: int) -> List[BloombergNewsItem]:
        """Get news from real Bloomberg Terminal API."""
        # Implementation would use Bloomberg News API
        # This is a placeholder - full implementation would require news service setup
        raise NotImplementedError("Real Bloomberg news not implemented in MVP")

    async def get_fx_rates(self, currency_pairs: List[str]) -> List[BloombergDataPoint]:
        """
        Get current FX rates for currency pairs.

        Args:
            currency_pairs: List of currency pair tickers (e.g., ['USDJPY Curncy', 'EURUSD Curncy'])

        Returns:
            List of BloombergDataPoint objects with current rates
        """
        fields = ['PX_LAST', 'PX_BID', 'PX_ASK', 'CHG_PCT_1D']
        return await self.get_reference_data(currency_pairs, fields)

    async def get_interest_rates(self, rate_tickers: List[str]) -> List[BloombergDataPoint]:
        """
        Get current interest rates.

        Args:
            rate_tickers: List of rate tickers (e.g., ['USGG10YR Index', 'FDTR Index'])

        Returns:
            List of BloombergDataPoint objects with current rates
        """
        fields = ['PX_LAST', 'CHG_NET_1D', 'CHG_PCT_1D']
        return await self.get_reference_data(rate_tickers, fields)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        if self.connection_type == BloombergConnectionType.MOCK and self.session:
            return self.session.get_session_stats()
        else:
            return {
                "session_active": self.session is not None,
                "connection_type": self.connection_type.value,
                "daily_requests_used": self._daily_request_count,
                "daily_requests_remaining": self.config.max_daily_requests - self._daily_request_count,
                "session_duration_minutes": (
                    (datetime.utcnow() - self._session_start_time).total_seconds() / 60
                    if self._session_start_time else 0
                )
            }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Bloomberg service."""
        try:
            if not self.session:
                return {"status": "error", "message": "No active session"}

            # Test with a simple request
            test_result = await self.get_reference_data(['USDJPY Curncy'], ['PX_LAST'])

            if test_result:
                return {
                    "status": "healthy",
                    "connection_type": self.connection_type.value,
                    "test_request_successful": True,
                    "session_stats": self.get_session_stats()
                }
            else:
                return {"status": "degraded", "message": "Test request returned no data"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

# Convenience functions
async def create_bloomberg_service(use_mock: bool = None) -> BloombergService:
    """
    Create and initialize Bloomberg service.

    Args:
        use_mock: Force mock mode if True, auto-detect if None

    Returns:
        Initialized BloombergService
    """
    if use_mock is not None:
        connection_type = BloombergConnectionType.MOCK if use_mock else BloombergConnectionType.TERMINAL_API
        config = BloombergConfig(connection_type=connection_type)
        service = BloombergService(config)
    else:
        service = BloombergService()

    await service.start_session()
    return service

# Asia/G10 predefined security lists
ASIA_G10_FX_PAIRS = [
    'USDJPY Curncy',   # US Dollar / Japanese Yen
    'EURUSD Curncy',   # Euro / US Dollar
    'GBPUSD Curncy',   # British Pound / US Dollar
    'AUDUSD Curncy',   # Australian Dollar / US Dollar
    'USDCHF Curncy',   # US Dollar / Swiss Franc
    'USDCAD Curncy',   # US Dollar / Canadian Dollar
]

ASIA_G10_INTEREST_RATES = [
    'USGG10YR Index',  # US 10 Year Treasury
    'GDBR10 Index',    # German 10 Year Bund
    'GJGB10 Index',    # Japan 10 Year Government Bond
    'GUKG10 Index',    # UK 10 Year Gilt
    'FDTR Index',      # Federal Funds Target Rate
    'EURR002W Index',  # Euro Interbank Offered Rate
    'JYDR1T Curncy',   # Japan Discount Rate
]

# Export main classes and functions
__all__ = [
    'BloombergService', 'BloombergConfig', 'BloombergConnectionType',
    'BloombergAPIError', 'BloombergRateLimitError', 'BloombergConnectionError',
    'create_bloomberg_service', 'ASIA_G10_FX_PAIRS', 'ASIA_G10_INTEREST_RATES'
]