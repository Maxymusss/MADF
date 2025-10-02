# Message Models for MADF Inter-Agent Communication
# Bloomberg API Integration with File-Based JSON Messaging
# Created: 2025-09-21 | Story 1.1 Implementation

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Union, Dict, Any, List
from enum import Enum
import uuid

# Agent and Message Type Enums
class AgentType(str, Enum):
    PRODUCT_MANAGER = "product_manager"
    RESEARCH_AGENT_1 = "research_agent_1"
    RESEARCH_AGENT_2 = "research_agent_2"
    VALIDATOR_AGENT = "validator_agent"

class MessageType(str, Enum):
    TASK_ASSIGNMENT = "task_assignment"
    TASK_ACCEPTANCE = "task_acceptance"
    TASK_PROGRESS = "task_progress"
    RESEARCH_RESULT = "research_result"
    VALIDATION_REQUEST = "validation_request"
    VALIDATION_RESULT = "validation_result"
    ERROR_REPORT = "error_report"
    HEARTBEAT = "heartbeat"
    SYSTEM_STATUS = "system_status"

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(str, Enum):
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

# Bloomberg-specific data structures
class BloombergSecurity(BaseModel):
    """Bloomberg security identifier and metadata."""
    ticker: str = Field(..., description="Bloomberg ticker (e.g., 'USDJPY Curncy')")
    name: str = Field(..., description="Security name")
    market: str = Field(..., description="Market type (FX, Govt, Money Market)")
    currency: str = Field(..., description="Base currency")
    sector: Optional[str] = Field(None, description="Sector classification")

class BloombergDataPoint(BaseModel):
    """Single Bloomberg data point."""
    security: str = Field(..., description="Bloomberg ticker")
    field: str = Field(..., description="Bloomberg field (e.g., 'PX_LAST')")
    value: Union[float, str, int] = Field(..., description="Field value")
    timestamp: datetime = Field(..., description="Data timestamp")
    source: str = Field(default="BBG", description="Data source")
    status: str = Field(default="OK", description="Data status")

class BloombergNewsItem(BaseModel):
    """Bloomberg news item structure."""
    story_id: str = Field(..., description="Unique story identifier")
    headline: str = Field(..., description="News headline")
    summary: str = Field(..., description="News summary")
    datetime_published: datetime = Field(..., description="Publication timestamp")
    source: str = Field(..., description="News source")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    sentiment: str = Field(..., description="Sentiment analysis")
    securities_mentioned: List[str] = Field(default_factory=list, description="Related securities")
    categories: List[str] = Field(default_factory=list, description="News categories")

# Base Message Structure
class BaseMessage(BaseModel):
    """Base message structure for inter-agent communication."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message identifier")
    from_agent: AgentType = Field(..., alias="from", description="Source agent")
    to_agent: AgentType = Field(..., alias="to", description="Destination agent")
    type: MessageType = Field(..., description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    content: Dict[str, Any] = Field(..., description="Message payload")
    priority: Priority = Field(default=Priority.NORMAL, description="Message priority")
    reply_to: Optional[str] = Field(None, description="Parent message ID")
    timeout: Optional[int] = Field(None, description="Timeout in seconds")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Task Assignment Message Content
class TaskAssignmentContent(BaseModel):
    """Content for task assignment messages."""
    task_type: str = Field(..., description="Type of task (e.g., 'bloomberg_research')")
    focus_area: str = Field(..., description="Research focus (e.g., 'Asia/G10 FX')")
    target_securities: List[str] = Field(..., description="Bloomberg tickers to research")
    bloomberg_fields: List[str] = Field(..., description="Bloomberg fields to retrieve")
    timeframe: str = Field(..., description="Time period for analysis")
    data_sources: List[str] = Field(default=["bloomberg"], description="Data sources to use")
    deadline: datetime = Field(..., description="Task completion deadline")
    output_format: str = Field(default="structured_json", description="Expected output format")
    special_instructions: Optional[str] = Field(None, description="Additional instructions")
    bloomberg_limits: Dict[str, int] = Field(
        default_factory=lambda: {"max_api_calls": 1000, "max_real_time_fields": 100},
        description="Bloomberg API usage limits"
    )

# Task Acceptance Message Content
class TaskAcceptanceContent(BaseModel):
    """Content for task acceptance messages."""
    task_id: str = Field(..., description="Reference to original task message_id")
    status: TaskStatus = Field(..., description="Acceptance status")
    estimated_completion: datetime = Field(..., description="Estimated completion time")
    agent_capacity: float = Field(..., ge=0.0, le=1.0, description="Current load percentage")
    bloomberg_session_status: str = Field(..., description="Bloomberg connection status")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")
    resource_requirements: Dict[str, Any] = Field(
        default_factory=dict, description="Required resources"
    )

# Research Result Message Content
class ResearchResultContent(BaseModel):
    """Content for research result messages."""
    task_id: str = Field(..., description="Reference to original task")
    status: TaskStatus = Field(..., description="Task completion status")
    execution_time_minutes: float = Field(..., description="Actual execution time")
    bloomberg_api_calls_used: int = Field(..., description="Bloomberg API calls consumed")
    data_points_collected: int = Field(..., description="Number of data points retrieved")
    sources_accessed: List[str] = Field(..., description="Data sources used")
    key_findings: List[str] = Field(..., description="Summary of key findings")
    bloomberg_data: List[BloombergDataPoint] = Field(..., description="Raw Bloomberg data")
    news_items: List[BloombergNewsItem] = Field(default_factory=list, description="Relevant news")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Result confidence")
    data_freshness_hours: float = Field(..., description="Age of newest data")
    warnings: List[str] = Field(default_factory=list, description="Warnings or limitations")
    bloomberg_session_stats: Dict[str, Any] = Field(
        default_factory=dict, description="Bloomberg session statistics"
    )

# Validation Request Message Content
class ValidationRequestContent(BaseModel):
    """Content for validation request messages."""
    research_results_to_validate: List[str] = Field(..., description="Message IDs to validate")
    validation_type: str = Field(..., description="Type of validation required")
    validation_sources: List[str] = Field(..., description="Sources for validation")
    priority_areas: List[str] = Field(..., description="Focus areas for validation")
    deadline: datetime = Field(..., description="Validation deadline")
    bloomberg_cross_check: bool = Field(default=True, description="Use Bloomberg for cross-validation")
    confidence_threshold: float = Field(default=0.8, description="Minimum confidence required")

# Validation Issue Structure
class ValidationIssue(BaseModel):
    """Individual validation issue."""
    issue_type: str = Field(..., description="Type of issue found")
    severity: str = Field(..., description="Issue severity level")
    description: str = Field(..., description="Detailed description")
    affected_data: Dict[str, Any] = Field(..., description="Affected data points")
    recommendation: str = Field(..., description="Recommended action")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in finding")
    bloomberg_reference: Optional[str] = Field(None, description="Bloomberg reference data")

# Validation Result Message Content
class ValidationResultContent(BaseModel):
    """Content for validation result messages."""
    validation_id: str = Field(..., description="Reference to validation request")
    research_results_validated: List[str] = Field(..., description="Validated message IDs")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    issues_found: List[ValidationIssue] = Field(..., description="Issues identified")
    validated_findings: List[str] = Field(..., description="Confirmed findings")
    execution_time_minutes: float = Field(..., description="Validation execution time")
    sources_consulted: List[str] = Field(..., description="Validation sources used")
    bloomberg_validation_stats: Dict[str, Any] = Field(
        default_factory=dict, description="Bloomberg validation statistics"
    )
    cross_reference_score: float = Field(..., ge=0.0, le=1.0, description="Cross-reference quality")

# Error Report Message Content
class ErrorReportContent(BaseModel):
    """Content for error report messages."""
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error description")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context")
    stack_trace: Optional[str] = Field(None, description="Stack trace if available")
    recovery_action: Optional[str] = Field(None, description="Recovery action taken")
    impact_level: str = Field(..., description="Impact severity")
    related_task_id: Optional[str] = Field(None, description="Related task ID")
    bloomberg_error_code: Optional[str] = Field(None, description="Bloomberg error code")
    retry_count: int = Field(default=0, description="Number of retries attempted")

# System Status Message Content
class SystemStatusContent(BaseModel):
    """Content for system status messages."""
    agent_status: str = Field(..., description="Agent health status")
    cpu_usage_percent: float = Field(..., description="CPU usage percentage")
    memory_usage_mb: float = Field(..., description="Memory usage in MB")
    active_tasks: int = Field(..., description="Number of active tasks")
    completed_tasks_today: int = Field(..., description="Tasks completed today")
    error_count_today: int = Field(..., description="Errors today")
    last_successful_operation: datetime = Field(..., description="Last successful operation")
    performance_metrics: Dict[str, float] = Field(..., description="Performance metrics")
    bloomberg_session_info: Dict[str, Any] = Field(
        default_factory=dict, description="Bloomberg session information"
    )

# Heartbeat Message Content
class HeartbeatContent(BaseModel):
    """Content for heartbeat messages."""
    agent_version: str = Field(default="1.0.0", description="Agent version")
    uptime_seconds: float = Field(..., description="Agent uptime in seconds")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    health_score: float = Field(..., ge=0.0, le=1.0, description="Agent health score")
    bloomberg_connection_status: str = Field(..., description="Bloomberg connection status")

# Message Factory for creating typed messages
class MessageFactory:
    """Factory for creating properly typed messages."""

    @staticmethod
    def create_task_assignment(
        from_agent: AgentType,
        to_agent: AgentType,
        content: TaskAssignmentContent,
        priority: Priority = Priority.NORMAL
    ) -> BaseMessage:
        """Create a task assignment message."""
        return BaseMessage(
            **{"from": from_agent},
            to=to_agent,
            type=MessageType.TASK_ASSIGNMENT,
            content=content.dict(),
            priority=priority
        )

    @staticmethod
    def create_research_result(
        from_agent: AgentType,
        content: ResearchResultContent,
        reply_to: str = None
    ) -> BaseMessage:
        """Create a research result message."""
        return BaseMessage(
            **{"from": from_agent},
            to=AgentType.PRODUCT_MANAGER,
            type=MessageType.RESEARCH_RESULT,
            content=content.dict(),
            reply_to=reply_to
        )

    @staticmethod
    def create_validation_request(
        from_agent: AgentType,
        to_agent: AgentType,
        content: ValidationRequestContent,
        priority: Priority = Priority.HIGH
    ) -> BaseMessage:
        """Create a validation request message."""
        return BaseMessage(
            **{"from": from_agent},
            to=to_agent,
            type=MessageType.VALIDATION_REQUEST,
            content=content.dict(),
            priority=priority
        )

    @staticmethod
    def create_error_report(
        from_agent: AgentType,
        content: ErrorReportContent,
        priority: Priority = Priority.HIGH
    ) -> BaseMessage:
        """Create an error report message."""
        return BaseMessage(
            **{"from": from_agent},
            to=AgentType.PRODUCT_MANAGER,
            type=MessageType.ERROR_REPORT,
            content=content.dict(),
            priority=priority
        )

    @staticmethod
    def create_heartbeat(
        from_agent: AgentType,
        content: HeartbeatContent
    ) -> BaseMessage:
        """Create a heartbeat message."""
        return BaseMessage(
            **{"from": from_agent},
            to=AgentType.PRODUCT_MANAGER,
            type=MessageType.HEARTBEAT,
            content=content.dict(),
            priority=Priority.LOW
        )

# Validation utilities
def validate_bloomberg_ticker(ticker: str) -> bool:
    """Validate Bloomberg ticker format."""
    if not ticker:
        return False

    # Common Bloomberg ticker patterns
    patterns = [
        r'^\w+\s+Curncy$',      # Currency: USDJPY Curncy
        r'^\w+\s+Index$',       # Index: USGG10YR Index
        r'^\w+\s+Equity$',      # Equity: AAPL US Equity
        r'^\w+\s+Corp$',        # Corporate bond
        r'^\w+\s+Govt$',        # Government bond
    ]

    import re
    return any(re.match(pattern, ticker) for pattern in patterns)

def validate_bloomberg_field(field: str) -> bool:
    """Validate Bloomberg field name."""
    common_fields = {
        'PX_LAST', 'PX_BID', 'PX_ASK', 'PX_HIGH', 'PX_LOW',
        'PX_OPEN', 'PX_VOLUME', 'CHG_PCT_1D', 'CHG_NET_1D',
        'LAST_PRICE', 'BID', 'ASK', 'HIGH', 'LOW', 'OPEN',
        'VOLUME', 'DAY_CHG_PCT', 'DAY_CHG_NET', 'SECURITY_NAME',
        'CRNCY', 'MARKET_SECTOR_DES', 'COUNTRY', 'GICS_SECTOR_NAME'
    }
    return field.upper() in common_fields

# Export all models
__all__ = [
    'AgentType', 'MessageType', 'Priority', 'TaskStatus',
    'BloombergSecurity', 'BloombergDataPoint', 'BloombergNewsItem',
    'BaseMessage', 'TaskAssignmentContent', 'TaskAcceptanceContent',
    'ResearchResultContent', 'ValidationRequestContent', 'ValidationIssue',
    'ValidationResultContent', 'ErrorReportContent', 'SystemStatusContent',
    'HeartbeatContent', 'MessageFactory', 'validate_bloomberg_ticker',
    'validate_bloomberg_field'
]