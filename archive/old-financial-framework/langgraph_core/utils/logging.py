"""
Structured logging setup for LangGraph workflow
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    workflow_id: str = None
) -> logging.Logger:
    """
    Set up structured logging for LangGraph workflow

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        workflow_id: Optional workflow ID for log context

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("langgraph_core")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    log_format = "%(asctime)s - %(name)s - %(levelname)s"
    if workflow_id:
        log_format += f" - [WF:{workflow_id}]"
    log_format += " - %(message)s"

    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for files
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def create_workflow_logger(workflow_id: str) -> logging.Logger:
    """
    Create a logger for a specific workflow

    Args:
        workflow_id: Unique workflow identifier

    Returns:
        Configured logger for the workflow
    """
    # Create log file path
    log_dir = Path("logs/agents")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"workflow_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    return setup_logging(
        log_level="INFO",
        log_file=str(log_file),
        workflow_id=workflow_id
    )