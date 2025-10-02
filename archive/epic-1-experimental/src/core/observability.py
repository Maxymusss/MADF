"""
LangSmith Integration for Tracing and Monitoring

Provides comprehensive observability for multiagent workflows
"""

import os
from typing import Dict, Any, Optional
from langsmith import Client


def get_langsmith_config() -> Dict[str, str]:
    """
    Get LangSmith configuration for tracing

    Returns:
        Dict containing project and API key configuration
    """
    return {
        "project": os.getenv("LANGSMITH_PROJECT", "madf-multiagent-framework"),
        "api_key": os.getenv("LANGSMITH_API_KEY", "test-api-key-for-development"),
        "endpoint": os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"),
        "tracing_enabled": os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
    }


def initialize_langsmith_tracing() -> Optional[Client]:
    """
    Initialize LangSmith tracing client

    Returns:
        LangSmith client if successful, None otherwise
    """
    config = get_langsmith_config()

    if not config["tracing_enabled"]:
        return None

    try:
        # Set environment variables for LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = config["project"]
        os.environ["LANGCHAIN_API_KEY"] = config["api_key"]
        os.environ["LANGCHAIN_ENDPOINT"] = config["endpoint"]

        # Initialize client
        client = Client(
            api_url=config["endpoint"],
            api_key=config["api_key"]
        )

        return client

    except Exception as e:
        print(f"Warning: Failed to initialize LangSmith tracing: {e}")
        return None


def create_workflow_run_metadata(
    workflow_id: str,
    agent_sequence: list,
    task_description: str
) -> Dict[str, Any]:
    """
    Create metadata for workflow run tracking

    Args:
        workflow_id: Unique identifier for workflow
        agent_sequence: List of agents involved in workflow
        task_description: Description of task being processed

    Returns:
        Dict containing metadata for tracing
    """
    return {
        "workflow_id": workflow_id,
        "agent_sequence": agent_sequence,
        "task_description": task_description,
        "framework": "MADF",
        "version": "1.0.0",
        "multiagent": True,
        "total_agents": len(agent_sequence)
    }