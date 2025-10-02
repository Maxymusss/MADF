# File-Based Message Handler for MADF Inter-Agent Communication
# Atomic file operations with Bloomberg integration
# Created: 2025-09-21 | Story 1.1 Implementation

import asyncio
import aiofiles
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
import uuid
import tempfile
import shutil

from .models import (
    BaseMessage, AgentType, MessageType, Priority,
    TaskAssignmentContent, TaskAcceptanceContent, ResearchResultContent,
    ValidationRequestContent, ValidationResultContent, ErrorReportContent,
    SystemStatusContent, HeartbeatContent, MessageFactory
)

logger = logging.getLogger(__name__)

class MessageHandlerError(Exception):
    """Message handler specific errors."""
    pass

class MessageHandler:
    """
    File-based message handler for inter-agent communication.
    Implements atomic file operations for reliable message delivery.
    """

    def __init__(self, message_dir: Path, agent_type: AgentType, poll_interval: float = 1.0):
        self.message_dir = Path(message_dir)
        self.agent_type = agent_type
        self.poll_interval = poll_interval

        # Directory structure
        self.inbox = self.message_dir / "inbox" / agent_type.value
        self.outbox = self.message_dir / "outbox" / agent_type.value
        self.processed = self.message_dir / "processed" / agent_type.value
        self.failed = self.message_dir / "failed" / agent_type.value

        # Create directories
        self._create_directories()

        # Message processing state
        self._running = False
        self._message_callbacks: Dict[MessageType, List[Callable]] = {}
        self._processed_message_ids = set()

        logger.info(f"Message handler initialized for {agent_type.value}")

    def _create_directories(self):
        """Create all required directories."""
        for directory in [self.inbox, self.outbox, self.processed, self.failed]:
            directory.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Message directories created for {self.agent_type.value}")

    async def send_message(self, message: BaseMessage, target_agent: AgentType = None):
        """
        Send message to another agent using atomic file operations.

        Args:
            message: Message to send
            target_agent: Override target agent (uses message.to_agent if None)
        """
        try:
            # Determine target agent
            target = target_agent or message.to_agent

            # Target inbox directory
            target_inbox = self.message_dir / "inbox" / target.value
            target_inbox.mkdir(parents=True, exist_ok=True)

            # Create unique filename
            filename = f"{message.message_id}.json"

            # Atomic write using temporary file
            temp_file = target_inbox / f".tmp_{filename}_{uuid.uuid4().hex[:8]}"
            final_file = target_inbox / filename

            # Write to temporary file first
            message_data = message.dict(by_alias=True)
            message_data['timestamp'] = message.timestamp.isoformat()

            async with aiofiles.open(temp_file, 'w') as f:
                await f.write(json.dumps(message_data, indent=2, default=str))

            # Atomic rename
            temp_file.rename(final_file)

            # Also save to our outbox for audit trail
            outbox_file = self.outbox / filename
            shutil.copy2(final_file, outbox_file)

            logger.debug(f"Message sent: {message.message_id} -> {target.value}")

        except Exception as e:
            logger.error(f"Failed to send message {message.message_id}: {e}")
            raise MessageHandlerError(f"Failed to send message: {e}")

    async def receive_messages(self, limit: int = None) -> List[BaseMessage]:
        """
        Receive all pending messages from inbox.

        Args:
            limit: Maximum number of messages to process (None for all)

        Returns:
            List of received messages
        """
        messages = []
        processed_count = 0

        try:
            # Get all JSON files in inbox, sorted by creation time
            message_files = sorted(
                [f for f in self.inbox.glob("*.json") if not f.name.startswith('.tmp_')],
                key=lambda x: x.stat().st_ctime
            )

            for message_file in message_files:
                if limit and processed_count >= limit:
                    break

                try:
                    # Read message
                    async with aiofiles.open(message_file, 'r') as f:
                        content = await f.read()

                    message_data = json.loads(content)

                    # Parse timestamp
                    if 'timestamp' in message_data:
                        message_data['timestamp'] = datetime.fromisoformat(
                            message_data['timestamp'].replace('Z', '+00:00')
                        )

                    # Create message object
                    message = BaseMessage(**message_data)

                    # Check for duplicates
                    if message.message_id not in self._processed_message_ids:
                        messages.append(message)
                        self._processed_message_ids.add(message.message_id)

                        # Move to processed directory
                        processed_file = self.processed / message_file.name
                        message_file.rename(processed_file)

                        processed_count += 1
                        logger.debug(f"Message received: {message.message_id} from {message.from_agent}")

                    else:
                        # Duplicate message, move to processed
                        logger.warning(f"Duplicate message ignored: {message.message_id}")
                        processed_file = self.processed / f"dup_{message_file.name}"
                        message_file.rename(processed_file)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in message file {message_file}: {e}")
                    self._move_to_failed(message_file, f"JSON decode error: {e}")

                except Exception as e:
                    logger.error(f"Error processing message file {message_file}: {e}")
                    self._move_to_failed(message_file, f"Processing error: {e}")

        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            raise MessageHandlerError(f"Failed to receive messages: {e}")

        if messages:
            logger.info(f"Received {len(messages)} messages")

        return messages

    def _move_to_failed(self, message_file: Path, error_reason: str):
        """Move failed message to failed directory with error info."""
        try:
            failed_file = self.failed / f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{message_file.name}"

            # Create error info file
            error_info = {
                "original_file": message_file.name,
                "error_reason": error_reason,
                "timestamp": datetime.utcnow().isoformat(),
                "agent": self.agent_type.value
            }

            error_file = self.failed / f"{failed_file.stem}_error.json"
            with open(error_file, 'w') as f:
                json.dump(error_info, f, indent=2)

            # Move original file
            message_file.rename(failed_file)

        except Exception as e:
            logger.error(f"Failed to move message to failed directory: {e}")

    def register_message_callback(self, message_type: MessageType, callback: Callable[[BaseMessage], None]):
        """
        Register callback for specific message type.

        Args:
            message_type: Type of message to handle
            callback: Callback function to execute
        """
        if message_type not in self._message_callbacks:
            self._message_callbacks[message_type] = []

        self._message_callbacks[message_type].append(callback)
        logger.debug(f"Registered callback for {message_type.value}")

    async def start_message_loop(self):
        """Start the message processing loop."""
        if self._running:
            logger.warning("Message loop already running")
            return

        self._running = True
        logger.info(f"Starting message loop for {self.agent_type.value}")

        try:
            while self._running:
                # Receive messages
                messages = await self.receive_messages()

                # Process each message
                for message in messages:
                    await self._process_message(message)

                # Wait before next poll
                await asyncio.sleep(self.poll_interval)

        except Exception as e:
            logger.error(f"Message loop error: {e}")
            raise

    async def stop_message_loop(self):
        """Stop the message processing loop."""
        self._running = False
        logger.info(f"Message loop stopped for {self.agent_type.value}")

    async def _process_message(self, message: BaseMessage):
        """Process individual message by calling registered callbacks."""
        try:
            # Check if we have callbacks for this message type
            if message.type in self._message_callbacks:
                for callback in self._message_callbacks[message.type]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(message)
                        else:
                            callback(message)
                    except Exception as e:
                        logger.error(f"Callback error for message {message.message_id}: {e}")

                        # Send error report if callback fails
                        await self._send_error_report(
                            f"Callback error for {message.type.value}",
                            str(e),
                            {"message_id": message.message_id, "from_agent": message.from_agent.value}
                        )

        except Exception as e:
            logger.error(f"Error processing message {message.message_id}: {e}")

    async def _send_error_report(self, error_type: str, error_message: str, context: Dict[str, Any]):
        """Send error report to Product Manager."""
        try:
            error_content = ErrorReportContent(
                error_type=error_type,
                error_message=error_message,
                context=context,
                impact_level="medium"
            )

            error_msg = MessageFactory.create_error_report(
                from_agent=self.agent_type,
                content=error_content
            )

            await self.send_message(error_msg, AgentType.PRODUCT_MANAGER)

        except Exception as e:
            logger.error(f"Failed to send error report: {e}")

    async def send_heartbeat(self, uptime_seconds: float, health_score: float = 1.0,
                           bloomberg_status: str = "unknown"):
        """Send heartbeat message to Product Manager."""
        try:
            heartbeat_content = HeartbeatContent(
                uptime_seconds=uptime_seconds,
                last_activity=datetime.utcnow(),
                health_score=health_score,
                bloomberg_connection_status=bloomberg_status
            )

            heartbeat_msg = MessageFactory.create_heartbeat(
                from_agent=self.agent_type,
                content=heartbeat_content
            )

            await self.send_message(heartbeat_msg, AgentType.PRODUCT_MANAGER)

        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")

    async def wait_for_message(self, message_type: MessageType, timeout_seconds: int = 30) -> Optional[BaseMessage]:
        """
        Wait for a specific type of message.

        Args:
            message_type: Type of message to wait for
            timeout_seconds: Maximum time to wait

        Returns:
            Received message or None if timeout
        """
        start_time = datetime.utcnow()
        timeout = timedelta(seconds=timeout_seconds)

        while datetime.utcnow() - start_time < timeout:
            messages = await self.receive_messages()

            for message in messages:
                if message.type == message_type:
                    return message

                # Process other messages
                await self._process_message(message)

            await asyncio.sleep(0.5)  # Short poll for waiting

        return None

    def cleanup_old_messages(self, days_to_keep: int = 7):
        """Clean up old processed and failed messages."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        for directory in [self.processed, self.failed]:
            cleaned_count = 0
            for message_file in directory.glob("*.json"):
                try:
                    file_time = datetime.fromtimestamp(message_file.stat().st_ctime)
                    if file_time < cutoff_date:
                        message_file.unlink()
                        cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to clean up {message_file}: {e}")

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old messages from {directory.name}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get message handling statistics."""
        try:
            stats = {
                "agent_type": self.agent_type.value,
                "inbox_count": len(list(self.inbox.glob("*.json"))),
                "outbox_count": len(list(self.outbox.glob("*.json"))),
                "processed_count": len(list(self.processed.glob("*.json"))),
                "failed_count": len(list(self.failed.glob("*.json"))),
                "running": self._running,
                "processed_message_ids": len(self._processed_message_ids),
                "registered_callbacks": len(self._message_callbacks)
            }
            return stats

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}

# Convenience functions
async def create_message_handler(message_dir: Path, agent_type: AgentType) -> MessageHandler:
    """Create and initialize a message handler."""
    return MessageHandler(message_dir, agent_type)

def create_data_directories(base_dir: Path):
    """Create the complete data directory structure for MADF."""
    directories = [
        "messages/inbox/product_manager",
        "messages/inbox/research_agent_1",
        "messages/inbox/research_agent_2",
        "messages/inbox/validator_agent",
        "messages/outbox/product_manager",
        "messages/outbox/research_agent_1",
        "messages/outbox/research_agent_2",
        "messages/outbox/validator_agent",
        "messages/processed/product_manager",
        "messages/processed/research_agent_1",
        "messages/processed/research_agent_2",
        "messages/processed/validator_agent",
        "messages/failed/product_manager",
        "messages/failed/research_agent_1",
        "messages/failed/research_agent_2",
        "messages/failed/validator_agent",
        "cache",
        "state",
        "logs"
    ]

    for dir_path in directories:
        (base_dir / dir_path).mkdir(parents=True, exist_ok=True)

    logger.info(f"MADF data directories created in {base_dir}")

# Export main classes
__all__ = [
    'MessageHandler', 'MessageHandlerError',
    'create_message_handler', 'create_data_directories'
]