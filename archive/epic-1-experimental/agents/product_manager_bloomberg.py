"""
Enhanced Product Manager Agent - Bloomberg Integration
Multi-Agent Financial Research Framework with BMAD Support
Created: 2025-09-21 | Story 1.1 Implementation
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid
import aiofiles

# Import MADF common modules
from python.common.models import (
    AgentType, MessageType, Priority, TaskStatus,
    TaskAssignmentContent, ResearchResultContent, ValidationRequestContent,
    ValidationResultContent, ErrorReportContent, HeartbeatContent,
    MessageFactory, BloombergDataPoint, BloombergNewsItem
)
from python.common.messaging import MessageHandler, create_data_directories
from python.common.bloomberg_service import (
    BloombergService, create_bloomberg_service,
    ASIA_G10_FX_PAIRS, ASIA_G10_INTEREST_RATES
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedProductManagerAgent:
    """
    Enhanced Product Manager Agent with Bloomberg integration and BMAD framework support.
    Orchestrates multi-agent financial research workflow using file-based messaging.
    """

    def __init__(self, workspace_dir: str = "data", use_bloomberg_mock: bool = True):
        self.workspace_dir = Path(workspace_dir)
        self.use_bloomberg_mock = use_bloomberg_mock

        # Create data directory structure
        create_data_directories(self.workspace_dir)

        # Initialize message handler
        self.message_handler = MessageHandler(
            self.workspace_dir / "messages",
            AgentType.PRODUCT_MANAGER,
            poll_interval=float(os.getenv('MESSAGE_POLL_INTERVAL', '1.0'))
        )

        # Bloomberg service (will be initialized on startup)
        self.bloomberg_service: Optional[BloombergService] = None

        # Agent state
        self.agent_id = f"pm_{uuid.uuid4().hex[:8]}"
        self.session_start_time = datetime.utcnow()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[str] = []
        self.agent_status = "initializing"

        # Performance tracking
        self.performance_metrics = {
            "tasks_assigned": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "bloomberg_api_calls": 0,
            "validation_requests": 0
        }

        # Error tracking for learning
        self.error_log_file = self.workspace_dir / "logs" / "product_manager_errors.json"
        self.performance_log_file = self.workspace_dir / "logs" / "performance_metrics.json"

        # Register message callbacks
        self._register_message_handlers()

        logger.info(f"Enhanced Product Manager Agent initialized: {self.agent_id}")
        logger.info(f"Workspace: {self.workspace_dir}")
        logger.info(f"Bloomberg mode: {'Mock' if use_bloomberg_mock else 'Real'}")

    def _register_message_handlers(self):
        """Register callbacks for different message types."""
        self.message_handler.register_message_callback(
            MessageType.RESEARCH_RESULT, self._handle_research_result
        )
        self.message_handler.register_message_callback(
            MessageType.VALIDATION_RESULT, self._handle_validation_result
        )
        self.message_handler.register_message_callback(
            MessageType.ERROR_REPORT, self._handle_error_report
        )
        self.message_handler.register_message_callback(
            MessageType.HEARTBEAT, self._handle_heartbeat
        )

        logger.debug("Message handlers registered")

    async def initialize(self):
        """Initialize the Product Manager agent services."""
        try:
            # Initialize Bloomberg service
            self.bloomberg_service = await create_bloomberg_service(use_mock=self.use_bloomberg_mock)

            # Perform health check
            health_status = await self.bloomberg_service.health_check()
            logger.info(f"Bloomberg service health: {health_status['status']}")

            self.agent_status = "ready"
            logger.info("Enhanced Product Manager Agent initialization complete")

        except Exception as e:
            self.agent_status = "error"
            logger.error(f"Failed to initialize Enhanced Product Manager Agent: {e}")
            raise

    async def shutdown(self):
        """Shutdown the Product Manager agent."""
        try:
            # Stop message loop
            await self.message_handler.stop_message_loop()

            # Stop Bloomberg session
            if self.bloomberg_service:
                await self.bloomberg_service.stop_session()

            # Save final performance metrics
            await self._save_performance_metrics()

            self.agent_status = "shutdown"
            logger.info("Enhanced Product Manager Agent shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def get_week_timeframe(self, ask_date: Optional[datetime] = None) -> tuple[datetime, datetime]:
        """
        Calculate the timeframe for 'this week' research.
        From Monday 8 days before ask_date including weekends.
        """
        if ask_date is None:
            ask_date = datetime.utcnow()

        # Find Monday 8 days before ask_date
        days_back = 8 + ask_date.weekday()  # Get to Monday, then go back 8 more days
        start_date = ask_date - timedelta(days=days_back)

        return start_date, ask_date

    async def create_bloomberg_research_task(self, task_id: str,
                                           focus_areas: List[str] = None,
                                           custom_securities: List[str] = None) -> TaskAssignmentContent:
        """
        Create a Bloomberg-based research task for Asia/G10 FX and rates.

        Args:
            task_id: Unique task identifier
            focus_areas: List of focus areas (default: ['fx', 'rates'])
            custom_securities: Custom Bloomberg tickers (default: Asia/G10 securities)

        Returns:
            TaskAssignmentContent object
        """
        if focus_areas is None:
            focus_areas = ['fx', 'rates']

        # Determine target securities based on focus areas
        target_securities = custom_securities or []
        bloomberg_fields = []

        if 'fx' in focus_areas:
            target_securities.extend(ASIA_G10_FX_PAIRS)
            bloomberg_fields.extend(['PX_LAST', 'PX_BID', 'PX_ASK', 'CHG_PCT_1D', 'PX_VOLUME'])

        if 'rates' in focus_areas:
            target_securities.extend(ASIA_G10_INTEREST_RATES)
            bloomberg_fields.extend(['PX_LAST', 'CHG_NET_1D', 'CHG_PCT_1D'])

        # Remove duplicates
        target_securities = list(set(target_securities))
        bloomberg_fields = list(set(bloomberg_fields))

        start_date, end_date = self.get_week_timeframe()

        task_content = TaskAssignmentContent(
            task_type="bloomberg_research",
            focus_area="Asia/G10 FX and Interest Rates",
            target_securities=target_securities,
            bloomberg_fields=bloomberg_fields,
            timeframe=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            data_sources=["bloomberg", "bloomberg_news"],
            deadline=datetime.utcnow() + timedelta(hours=2),
            output_format="structured_json",
            special_instructions=f"Focus on {', '.join(focus_areas)} markets with timing accuracy",
            bloomberg_limits={
                "max_api_calls": 5000,
                "max_real_time_fields": 200,
                "max_news_items": 50
            }
        )

        logger.info(f"Created Bloomberg research task: {task_id}")
        return task_content

    async def assign_research_task(self, task_content: TaskAssignmentContent,
                                 target_agents: List[AgentType] = None) -> List[str]:
        """
        Assign research task to available research agents.

        Args:
            task_content: Task assignment content
            target_agents: List of target agents (default: research agents 1 and 2)

        Returns:
            List of assigned task message IDs
        """
        if target_agents is None:
            target_agents = [AgentType.RESEARCH_AGENT_1, AgentType.RESEARCH_AGENT_2]

        assigned_message_ids = []

        for agent in target_agents:
            try:
                # Create task assignment message
                task_message = MessageFactory.create_task_assignment(
                    from_agent=AgentType.PRODUCT_MANAGER,
                    to_agent=agent,
                    content=task_content,
                    priority=Priority.HIGH
                )

                # Send message
                await self.message_handler.send_message(task_message, agent)

                # Track active task
                self.active_tasks[task_message.message_id] = {
                    "task_content": task_content.dict(),
                    "assigned_to": agent.value,
                    "assigned_at": datetime.utcnow(),
                    "status": TaskStatus.ASSIGNED,
                    "deadline": task_content.deadline
                }

                assigned_message_ids.append(task_message.message_id)
                self.performance_metrics["tasks_assigned"] += 1

                logger.info(f"Task assigned to {agent.value}: {task_message.message_id}")

            except Exception as e:
                logger.error(f"Failed to assign task to {agent.value}: {e}")
                await self._log_error("task_assignment_failed", str(e), {"agent": agent.value})

        return assigned_message_ids

    async def request_validation(self, research_result_ids: List[str]) -> str:
        """
        Request validation of research results from validator agent.

        Args:
            research_result_ids: List of research result message IDs to validate

        Returns:
            Validation request message ID
        """
        try:
            validation_content = ValidationRequestContent(
                research_results_to_validate=research_result_ids,
                validation_type="bloomberg_cross_check",
                validation_sources=["bloomberg", "reuters", "central_banks"],
                priority_areas=["timing_accuracy", "data_consistency", "source_reliability"],
                deadline=datetime.utcnow() + timedelta(hours=1),
                bloomberg_cross_check=True,
                confidence_threshold=0.85
            )

            validation_message = MessageFactory.create_validation_request(
                from_agent=AgentType.PRODUCT_MANAGER,
                to_agent=AgentType.VALIDATOR_AGENT,
                content=validation_content,
                priority=Priority.HIGH
            )

            await self.message_handler.send_message(validation_message)

            self.performance_metrics["validation_requests"] += 1

            logger.info(f"Validation requested: {validation_message.message_id}")
            return validation_message.message_id

        except Exception as e:
            logger.error(f"Failed to request validation: {e}")
            await self._log_error("validation_request_failed", str(e),
                                {"research_results": research_result_ids})
            raise

    async def _handle_research_result(self, message):
        """Handle incoming research result messages."""
        try:
            result_content = ResearchResultContent(**message.content)

            # Update task status
            if message.reply_to in self.active_tasks:
                task = self.active_tasks[message.reply_to]
                task["status"] = result_content.status
                task["completed_at"] = datetime.utcnow()
                task["result_message_id"] = message.message_id

                if result_content.status == TaskStatus.COMPLETED:
                    self.performance_metrics["tasks_completed"] += 1
                    self.completed_tasks.append(message.reply_to)
                elif result_content.status == TaskStatus.FAILED:
                    self.performance_metrics["tasks_failed"] += 1

            # Track Bloomberg API usage
            self.performance_metrics["bloomberg_api_calls"] += result_content.bloomberg_api_calls_used

            logger.info(f"Research result received from {message.from_agent}: {result_content.status}")
            logger.info(f"Data points: {result_content.data_points_collected}, "
                       f"API calls: {result_content.bloomberg_api_calls_used}")

        except Exception as e:
            logger.error(f"Error handling research result: {e}")
            await self._log_error("research_result_processing", str(e),
                                {"message_id": message.message_id})

    async def _handle_validation_result(self, message):
        """Handle incoming validation result messages."""
        try:
            validation_content = ValidationResultContent(**message.content)

            logger.info(f"Validation result received: {validation_content.overall_confidence:.2f} confidence")
            logger.info(f"Issues found: {len(validation_content.issues_found)}")

            # Process validation issues
            for issue in validation_content.issues_found:
                if issue.severity in ['high', 'critical']:
                    logger.warning(f"Validation issue ({issue.severity}): {issue.description}")

        except Exception as e:
            logger.error(f"Error handling validation result: {e}")

    async def _handle_error_report(self, message):
        """Handle incoming error reports from agents."""
        try:
            error_content = ErrorReportContent(**message.content)

            logger.warning(f"Error report from {message.from_agent}: {error_content.error_type}")
            logger.warning(f"Message: {error_content.error_message}")

            # Log error for learning system
            await self._log_error(
                f"agent_error_{message.from_agent}",
                error_content.error_message,
                error_content.context
            )

        except Exception as e:
            logger.error(f"Error handling error report: {e}")

    async def _handle_heartbeat(self, message):
        """Handle heartbeat messages from agents."""
        try:
            heartbeat_content = HeartbeatContent(**message.content)

            logger.debug(f"Heartbeat from {message.from_agent}: "
                        f"health={heartbeat_content.health_score:.2f}")

        except Exception as e:
            logger.debug(f"Error handling heartbeat: {e}")

    async def wait_for_task_completion(self, task_ids: List[str],
                                     timeout_minutes: int = 30) -> Dict[str, Any]:
        """
        Wait for specified tasks to complete.

        Args:
            task_ids: List of task message IDs to wait for
            timeout_minutes: Maximum time to wait

        Returns:
            Dictionary of completed task results
        """
        start_time = datetime.utcnow()
        timeout = timedelta(minutes=timeout_minutes)
        completed_tasks = {}

        while len(completed_tasks) < len(task_ids):
            if datetime.utcnow() - start_time > timeout:
                logger.warning(f"Timeout waiting for tasks. Completed: {len(completed_tasks)}/{len(task_ids)}")
                break

            # Check active tasks for completion
            for task_id in task_ids:
                if task_id not in completed_tasks and task_id in self.active_tasks:
                    task = self.active_tasks[task_id]

                    if task["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        completed_tasks[task_id] = task
                        logger.info(f"Task {task_id} completed with status: {task['status']}")

            # Process any pending messages
            await self.message_handler.receive_messages(limit=10)

            # Wait before next check
            await asyncio.sleep(5)

        return completed_tasks

    async def compile_weekly_report(self, completed_task_ids: List[str]) -> Dict[str, Any]:
        """
        Compile weekly financial research report from completed tasks.

        Args:
            completed_task_ids: List of completed task message IDs

        Returns:
            Compiled weekly report
        """
        start_date, end_date = self.get_week_timeframe()
        report_id = f"weekly_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Collect all research data
        all_bloomberg_data = []
        all_news_items = []
        all_key_findings = []
        total_api_calls = 0
        validation_confidence = 0.0

        for task_id in completed_task_ids:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]

                # This would be extracted from actual research result messages
                # For now, we'll create a placeholder structure
                # In real implementation, we'd parse the ResearchResultContent from messages

                total_api_calls += task.get("bloomberg_api_calls", 0)

        # Get current Bloomberg data for snapshot
        if self.bloomberg_service:
            try:
                # Get current FX rates
                fx_data = await self.bloomberg_service.get_fx_rates(ASIA_G10_FX_PAIRS[:3])  # Sample
                all_bloomberg_data.extend(fx_data)

                # Get current interest rates
                rates_data = await self.bloomberg_service.get_interest_rates(ASIA_G10_INTEREST_RATES[:3])  # Sample
                all_bloomberg_data.extend(rates_data)

                # Get recent news
                news_items = await self.bloomberg_service.get_news(
                    query="FX rates interest rates central bank",
                    start_date=start_date,
                    end_date=end_date,
                    max_results=10
                )
                all_news_items.extend(news_items)

            except Exception as e:
                logger.warning(f"Failed to get current Bloomberg data: {e}")

        # Compile final report
        final_report = {
            "report_id": report_id,
            "generated_at": datetime.utcnow().isoformat(),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "description": f"Week of {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            },
            "executive_summary": {
                "total_tasks_completed": len(completed_task_ids),
                "bloomberg_api_calls_used": total_api_calls,
                "data_points_collected": len(all_bloomberg_data),
                "news_items_analyzed": len(all_news_items),
                "overall_confidence": validation_confidence
            },
            "market_data": {
                "fx_rates": [dp.dict() for dp in all_bloomberg_data if 'Curncy' in dp.security],
                "interest_rates": [dp.dict() for dp in all_bloomberg_data if 'Index' in dp.security]
            },
            "news_summary": [news.dict() for news in all_news_items],
            "key_findings": all_key_findings,
            "performance_metrics": self.performance_metrics.copy(),
            "bloomberg_session_stats": self.bloomberg_service.get_session_stats() if self.bloomberg_service else {}
        }

        # Save report
        report_file = self.workspace_dir / "reports" / f"{report_id}.json"
        report_file.parent.mkdir(exist_ok=True)

        async with aiofiles.open(report_file, 'w') as f:
            await f.write(json.dumps(final_report, indent=2, default=str))

        logger.info(f"Weekly report compiled: {report_id}")
        return final_report

    async def _log_error(self, error_type: str, description: str, context: Dict[str, Any] = None):
        """
        Log errors for learning and improvement.
        """
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error_type,
            "description": description,
            "context": context or {},
            "agent_id": self.agent_id,
            "session_start": self.session_start_time.isoformat()
        }

        try:
            # Read existing errors
            errors = []
            if self.error_log_file.exists():
                async with aiofiles.open(self.error_log_file, 'r') as f:
                    content = await f.read()
                    errors = json.loads(content)

            errors.append(error_entry)

            # Keep only last 1000 errors
            if len(errors) > 1000:
                errors = errors[-1000:]

            # Save updated errors
            async with aiofiles.open(self.error_log_file, 'w') as f:
                await f.write(json.dumps(errors, indent=2, default=str))

            logger.warning(f"Error logged: {error_type} - {description}")

        except Exception as e:
            logger.error(f"Failed to log error: {e}")

    async def _save_performance_metrics(self):
        """Save current performance metrics."""
        try:
            metrics_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": self.agent_id,
                "session_duration_minutes": (datetime.utcnow() - self.session_start_time).total_seconds() / 60,
                "metrics": self.performance_metrics.copy(),
                "active_tasks_count": len(self.active_tasks),
                "completed_tasks_count": len(self.completed_tasks)
            }

            # Read existing metrics
            all_metrics = []
            if self.performance_log_file.exists():
                async with aiofiles.open(self.performance_log_file, 'r') as f:
                    content = await f.read()
                    all_metrics = json.loads(content)

            all_metrics.append(metrics_entry)

            # Save updated metrics
            async with aiofiles.open(self.performance_log_file, 'w') as f:
                await f.write(json.dumps(all_metrics, indent=2, default=str))

            logger.debug("Performance metrics saved")

        except Exception as e:
            logger.error(f"Failed to save performance metrics: {e}")

    async def execute_weekly_research_workflow(self, focus_areas: List[str] = None) -> Dict[str, Any]:
        """
        Main orchestration method for weekly FX/rates research using Bloomberg.

        Args:
            focus_areas: List of focus areas (default: ['fx', 'rates'])

        Returns:
            Weekly research report
        """
        if focus_areas is None:
            focus_areas = ['fx', 'rates']

        workflow_id = f"weekly_research_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        try:
            logger.info(f"Starting weekly research workflow: {workflow_id}")

            # Step 1: Create Bloomberg research task
            task_content = await self.create_bloomberg_research_task(
                workflow_id, focus_areas
            )

            # Step 2: Assign tasks to research agents
            assigned_task_ids = await self.assign_research_task(
                task_content, [AgentType.RESEARCH_AGENT_1, AgentType.RESEARCH_AGENT_2]
            )

            logger.info(f"Tasks assigned: {len(assigned_task_ids)} research agents")

            # Step 3: Wait for research completion
            logger.info("Waiting for research agents to complete...")
            completed_tasks = await self.wait_for_task_completion(
                assigned_task_ids, timeout_minutes=30
            )

            # Step 4: Request validation if we have results
            validation_message_id = None
            if completed_tasks:
                completed_result_ids = [
                    task.get("result_message_id") for task in completed_tasks.values()
                    if task.get("result_message_id")
                ]

                if completed_result_ids:
                    logger.info("Requesting validation of research results...")
                    validation_message_id = await self.request_validation(completed_result_ids)

                    # Wait for validation to complete
                    if validation_message_id:
                        await self.wait_for_task_completion([validation_message_id], timeout_minutes=15)

            # Step 5: Compile final weekly report
            final_report = await self.compile_weekly_report(list(completed_tasks.keys()))

            # Step 6: Save performance metrics
            await self._save_performance_metrics()

            logger.info(f"Weekly research workflow completed: {workflow_id}")
            return final_report

        except Exception as e:
            await self._log_error("workflow_execution", str(e), {"workflow_id": workflow_id})
            logger.error(f"Workflow execution failed: {e}")
            return {
                "status": "failed",
                "workflow_id": workflow_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def start_agent_loop(self):
        """Start the main agent message processing loop."""
        try:
            logger.info("Starting Enhanced Product Manager agent main loop")

            # Start message processing loop
            await self.message_handler.start_message_loop()

        except Exception as e:
            logger.error(f"Agent loop error: {e}")
            await self._log_error("agent_loop_error", str(e), {})
            raise

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            "agent_id": self.agent_id,
            "status": self.agent_status,
            "session_duration_minutes": (datetime.utcnow() - self.session_start_time).total_seconds() / 60,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "performance_metrics": self.performance_metrics.copy(),
            "bloomberg_service": {
                "connected": self.bloomberg_service is not None,
                "connection_type": self.bloomberg_service.connection_type.value if self.bloomberg_service else None,
                "session_stats": self.bloomberg_service.get_session_stats() if self.bloomberg_service else {}
            },
            "message_handler_stats": self.message_handler.get_statistics()
        }


async def main():
    """Example usage of the Enhanced Product Manager Agent with Bloomberg integration."""

    # Initialize Enhanced Product Manager Agent
    pm_agent = EnhancedProductManagerAgent(use_bloomberg_mock=True)

    try:
        # Initialize services
        await pm_agent.initialize()

        # Print agent status
        status = pm_agent.get_agent_status()
        print("\n=== Enhanced Product Manager Agent Status ===")
        print(f"Agent ID: {status['agent_id']}")
        print(f"Status: {status['status']}")
        print(f"Bloomberg Connection: {status['bloomberg_service']['connection_type']}")

        # Execute weekly research workflow
        print("\n=== Starting Weekly Research Workflow ===")
        result = await pm_agent.execute_weekly_research_workflow(['fx', 'rates'])

        print("\n=== Weekly Research Results ===")
        print(f"Report ID: {result.get('report_id', 'Unknown')}")
        print(f"Period: {result.get('period', {}).get('description', 'Unknown')}")
        print(f"Tasks Completed: {result.get('executive_summary', {}).get('total_tasks_completed', 0)}")
        print(f"Bloomberg API Calls: {result.get('executive_summary', {}).get('bloomberg_api_calls_used', 0)}")
        print(f"Data Points: {result.get('executive_summary', {}).get('data_points_collected', 0)}")

        if result.get('status') == 'failed':
            print(f"Error: {result.get('error', 'Unknown error')}")

        # Print final agent metrics
        final_status = pm_agent.get_agent_status()
        print("\n=== Final Performance Metrics ===")
        for metric, value in final_status['performance_metrics'].items():
            print(f"{metric}: {value}")

    except Exception as e:
        print(f"\nError in main execution: {e}")

    finally:
        # Shutdown agent
        await pm_agent.shutdown()
        print("\nEnhanced Product Manager Agent shutdown complete")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())


# Export main class
__all__ = ['EnhancedProductManagerAgent']