"""
LangGraph WorkflowState Pydantic model for multi-agent coordination
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone


class WorkflowState(BaseModel):
    """Core state model for LangGraph workflow execution"""

    # Workflow tracking
    workflow_id: str = Field(..., description="Unique workflow identifier")
    current_agent: str = Field(..., description="Currently active agent")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # BMAD plan integration
    plan: Optional[Dict[str, Any]] = Field(None, description="Loaded BMAD plan")
    plan_approved: bool = Field(False, description="Human approval status")

    # Research data
    research_data: Optional[Dict[str, Any]] = Field(None, description="Collected news data")
    research_summary: Optional[Dict[str, Any]] = Field(None, description="Research processing summary")

    # Generated content
    generated_content: Optional[Dict[str, Any]] = Field(None, description="Commentary content")
    word_count: int = Field(0, description="Total word count")

    # Validation and delivery
    validation_status: Optional[str] = Field(None, description="PM agent validation result")
    output_path: Optional[str] = Field(None, description="Delivered file path")

    # Error tracking and recovery
    errors: List[str] = Field(default_factory=list, description="Error messages")
    retry_count: int = Field(0, description="Retry attempts")

    # Performance metrics
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")

    class Config:
        """Pydantic configuration for state management"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def add_error(self, error_message: str) -> None:
        """Add error message to state"""
        self.errors.append(f"{datetime.now(timezone.utc).isoformat()}: {error_message}")

    def set_current_agent(self, agent_name: str) -> None:
        """Update current agent and timestamp"""
        self.current_agent = agent_name
        self.timestamp = datetime.now(timezone.utc)

    def is_complete(self) -> bool:
        """Check if workflow is complete"""
        return (
            self.validation_status == "approved" and
            self.output_path is not None and
            len(self.errors) == 0
        )

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get workflow execution summary"""
        return {
            "workflow_id": self.workflow_id,
            "current_agent": self.current_agent,
            "timestamp": self.timestamp.isoformat(),
            "errors_count": len(self.errors),
            "retry_count": self.retry_count,
            "validation_status": self.validation_status,
            "is_complete": self.is_complete(),
            "metadata": self.metadata
        }