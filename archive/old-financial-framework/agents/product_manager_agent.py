"""
Product Manager Agent - Multi-Agent Financial Research Framework
Orchestrates research and validation agents for FX/rates market summaries
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# MCP-use integration for tool access
import subprocess
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductManagerAgent:
    """
    Product Manager Agent that orchestrates multi-agent financial research workflow
    Uses shared file system for agent communication and MCP-use for tool access
    """

    def __init__(self, workspace_dir: str = "agent_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)

        # Communication directories
        self.tasks_dir = self.workspace_dir / "tasks"
        self.results_dir = self.workspace_dir / "results"
        self.logs_dir = self.workspace_dir / "logs"

        # Create directories
        for dir_path in [self.tasks_dir, self.results_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)

        # Agent configuration
        self.research_agents = []
        self.validator_agent = None
        self.task_queue = []

        # Error tracking for learning
        self.error_log_file = self.logs_dir / "product_manager_errors.json"
        self.performance_log_file = self.logs_dir / "performance_metrics.json"

        logger.info(f"Product Manager Agent initialized with workspace: {self.workspace_dir}")

    def get_week_timeframe(self, ask_date: Optional[datetime] = None) -> tuple[datetime, datetime]:
        """
        Calculate the timeframe for 'this week' research
        From Saturday 8 days before ask_date to ask_date
        """
        if ask_date is None:
            ask_date = datetime.now()

        # Find Saturday 8 days before
        days_back = 8
        start_date = ask_date - timedelta(days=days_back)

        # Ensure we start from Saturday
        while start_date.weekday() != 5:  # 5 = Saturday
            start_date -= timedelta(days=1)

        return start_date, ask_date

    def create_research_task(self, task_id: str, regions: List[str] = None,
                           markets: List[str] = None) -> Dict[str, Any]:
        """
        Create a research task specification for FX/rates analysis
        """
        if regions is None:
            regions = ["Asia", "G10"]
        if markets is None:
            markets = ["currencies", "interest_rates"]

        start_date, end_date = self.get_week_timeframe()

        task_spec = {
            "task_id": task_id,
            "task_type": "financial_research",
            "created_at": datetime.now().isoformat(),
            "timeframe": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "description": f"Saturday {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            },
            "scope": {
                "regions": regions,
                "markets": markets,
                "focus": "qualitative_summary"
            },
            "requirements": {
                "source_types": ["news", "central_bank_communications", "market_commentary"],
                "reliable_sources": [
                    "Reuters", "Bloomberg", "WSJ", "Financial Times",
                    "JPM Research", "Citi Research", "Goldman Sachs Research",
                    "Federal Reserve", "ECB", "BOJ", "RBA", "PBOC"
                ],
                "output_format": "structured_summary"
            },
            "quality_criteria": {
                "timing_accuracy": "Events must be within specified timeframe",
                "source_attribution": "All claims must cite reliable sources",
                "factual_accuracy": "Cross-reference conflicting information",
                "completeness": "Cover major events and movements"
            }
        }

        # Save task to shared file system
        task_file = self.tasks_dir / f"{task_id}.json"
        with open(task_file, 'w') as f:
            json.dump(task_spec, f, indent=2)

        logger.info(f"Created research task: {task_id}")
        return task_spec

    def deploy_research_agents(self, task_id: str, num_agents: int = 2) -> List[str]:
        """
        Deploy multiple research agents with different approaches
        Returns list of agent IDs
        """
        agent_ids = []

        # Define different research strategies
        strategies = [
            {
                "name": "comprehensive_search",
                "description": "Broad web search across multiple news sources",
                "tools": ["WebSearch", "WebFetch"],
                "focus": "comprehensive_coverage"
            },
            {
                "name": "source_specific",
                "description": "Target specific financial news sources",
                "tools": ["WebFetch"],
                "focus": "authoritative_sources"
            },
            {
                "name": "central_bank_focus",
                "description": "Focus on central bank communications",
                "tools": ["WebFetch", "WebSearch"],
                "focus": "official_communications"
            }
        ]

        for i in range(min(num_agents, len(strategies))):
            agent_id = f"research_agent_{i+1}_{task_id}"
            strategy = strategies[i]

            # Create agent task file
            agent_task = {
                "agent_id": agent_id,
                "task_id": task_id,
                "strategy": strategy,
                "status": "assigned",
                "assigned_at": datetime.now().isoformat(),
                "mcp_tools_required": strategy["tools"]
            }

            agent_task_file = self.tasks_dir / f"agent_{agent_id}.json"
            with open(agent_task_file, 'w') as f:
                json.dump(agent_task, f, indent=2)

            agent_ids.append(agent_id)
            logger.info(f"Deployed research agent: {agent_id} with strategy: {strategy['name']}")

        return agent_ids

    def deploy_validator_agent(self, task_id: str, research_agent_ids: List[str]) -> str:
        """
        Deploy validator agent to fact-check research results
        """
        validator_id = f"validator_{task_id}"

        validator_task = {
            "agent_id": validator_id,
            "task_id": task_id,
            "type": "validation",
            "research_agents_to_validate": research_agent_ids,
            "validation_strategy": {
                "cross_reference_sources": True,
                "fact_check_claims": True,
                "timing_verification": True,
                "source_reliability_check": True
            },
            "status": "waiting_for_research",
            "assigned_at": datetime.now().isoformat(),
            "mcp_tools_required": ["WebFetch", "WebSearch"]
        }

        validator_task_file = self.tasks_dir / f"validator_{validator_id}.json"
        with open(validator_task_file, 'w') as f:
            json.dump(validator_task, f, indent=2)

        logger.info(f"Deployed validator agent: {validator_id}")
        return validator_id

    def check_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Check the status of an agent by reading its result file
        """
        result_file = self.results_dir / f"{agent_id}_result.json"

        if result_file.exists():
            with open(result_file, 'r') as f:
                return json.load(f)
        else:
            return {"status": "in_progress", "agent_id": agent_id}

    def wait_for_agents(self, agent_ids: List[str], timeout_minutes: int = 30) -> Dict[str, Any]:
        """
        Wait for all agents to complete their tasks
        """
        start_time = datetime.now()
        timeout = timedelta(minutes=timeout_minutes)

        completed_agents = {}

        while len(completed_agents) < len(agent_ids):
            if datetime.now() - start_time > timeout:
                logger.warning(f"Timeout waiting for agents. Completed: {len(completed_agents)}/{len(agent_ids)}")
                break

            for agent_id in agent_ids:
                if agent_id not in completed_agents:
                    status = self.check_agent_status(agent_id)
                    if status.get("status") in ["completed", "failed"]:
                        completed_agents[agent_id] = status
                        logger.info(f"Agent {agent_id} completed with status: {status.get('status')}")

            # Sleep before next check
            asyncio.sleep(10)

        return completed_agents

    def compile_final_summary(self, task_id: str, research_results: Dict[str, Any],
                            validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compile final research summary from all agent results
        """
        start_date, end_date = self.get_week_timeframe()

        final_summary = {
            "summary_id": f"fx_rates_summary_{task_id}",
            "created_at": datetime.now().isoformat(),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "scope": ["Asia", "G10", "currencies", "interest_rates"],
            "research_agents_involved": len(research_results),
            "validation_performed": validation_results is not None,
            "content": {
                "key_events": [],
                "currency_movements": [],
                "interest_rate_changes": [],
                "central_bank_actions": [],
                "market_outlook": ""
            },
            "quality_metrics": {
                "sources_cited": 0,
                "cross_references": 0,
                "timing_accuracy": "verified",
                "confidence_score": 0.0
            },
            "raw_research_data": research_results,
            "validation_data": validation_results
        }

        # Process research results into structured content
        for agent_id, result in research_results.items():
            if result.get("status") == "completed" and "findings" in result:
                # Extract and categorize findings
                findings = result["findings"]

                # This would be enhanced with NLP processing in production
                final_summary["content"]["key_events"].extend(
                    findings.get("events", [])
                )
                final_summary["content"]["currency_movements"].extend(
                    findings.get("fx_movements", [])
                )
                final_summary["quality_metrics"]["sources_cited"] += len(
                    findings.get("sources", [])
                )

        # Incorporate validation results
        if validation_results and validation_results.get("status") == "completed":
            validation_data = validation_results.get("validation_summary", {})
            final_summary["quality_metrics"]["cross_references"] = validation_data.get("cross_references_found", 0)
            final_summary["quality_metrics"]["confidence_score"] = validation_data.get("confidence_score", 0.5)

        # Save final summary
        summary_file = self.results_dir / f"final_summary_{task_id}.json"
        with open(summary_file, 'w') as f:
            json.dump(final_summary, f, indent=2)

        logger.info(f"Compiled final summary for task: {task_id}")
        return final_summary

    def log_error(self, error_type: str, description: str, context: Dict[str, Any] = None):
        """
        Log errors for learning and improvement
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "description": description,
            "context": context or {},
            "session_id": getattr(self, 'current_session_id', 'unknown')
        }

        # Read existing errors
        errors = []
        if self.error_log_file.exists():
            with open(self.error_log_file, 'r') as f:
                errors = json.load(f)

        errors.append(error_entry)

        # Keep only last 1000 errors
        if len(errors) > 1000:
            errors = errors[-1000:]

        # Save updated errors
        with open(self.error_log_file, 'w') as f:
            json.dump(errors, f, indent=2)

        logger.warning(f"Logged error: {error_type} - {description}")

    def execute_fx_rates_research(self, custom_regions: List[str] = None,
                                custom_markets: List[str] = None) -> Dict[str, Any]:
        """
        Main orchestration method for FX/rates research
        """
        # Generate unique task ID
        task_id = f"fx_rates_{int(datetime.now().timestamp())}"
        self.current_session_id = task_id

        try:
            logger.info(f"Starting FX/rates research workflow: {task_id}")

            # Step 1: Create research task specification
            task_spec = self.create_research_task(task_id, custom_regions, custom_markets)

            # Step 2: Deploy research agents
            research_agent_ids = self.deploy_research_agents(task_id, num_agents=2)

            # Step 3: Deploy validator agent
            validator_id = self.deploy_validator_agent(task_id, research_agent_ids)

            # Step 4: Wait for research agents to complete
            logger.info("Waiting for research agents to complete...")
            research_results = self.wait_for_agents(research_agent_ids, timeout_minutes=20)

            # Step 5: Wait for validator to complete
            logger.info("Waiting for validator agent to complete...")
            validator_results = self.wait_for_agents([validator_id], timeout_minutes=10)
            validator_result = validator_results.get(validator_id, {})

            # Step 6: Compile final summary
            final_summary = self.compile_final_summary(
                task_id, research_results, validator_result
            )

            # Step 7: Log performance metrics
            self.log_performance_metrics(task_id, len(research_agent_ids), final_summary)

            logger.info(f"FX/rates research workflow completed: {task_id}")
            return final_summary

        except Exception as e:
            self.log_error("workflow_execution", str(e), {"task_id": task_id})
            logger.error(f"Workflow execution failed: {e}")
            return {
                "status": "failed",
                "task_id": task_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def log_performance_metrics(self, task_id: str, num_agents: int, final_summary: Dict[str, Any]):
        """
        Log performance metrics for continuous improvement
        """
        metrics = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "agents_deployed": num_agents,
            "sources_cited": final_summary.get("quality_metrics", {}).get("sources_cited", 0),
            "confidence_score": final_summary.get("quality_metrics", {}).get("confidence_score", 0),
            "cross_references": final_summary.get("quality_metrics", {}).get("cross_references", 0),
            "completion_status": final_summary.get("status", "unknown")
        }

        # Read existing metrics
        all_metrics = []
        if self.performance_log_file.exists():
            with open(self.performance_log_file, 'r') as f:
                all_metrics = json.load(f)

        all_metrics.append(metrics)

        # Save updated metrics
        with open(self.performance_log_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)

        logger.info(f"Logged performance metrics for task: {task_id}")


def main():
    """Example usage of the Product Manager Agent"""

    # Initialize Product Manager Agent
    pm_agent = ProductManagerAgent()

    # Execute FX/rates research workflow
    result = pm_agent.execute_fx_rates_research()

    print("\n=== FX/Rates Research Results ===")
    print(f"Task ID: {result.get('summary_id', 'Unknown')}")
    print(f"Status: {result.get('status', 'Unknown')}")
    print(f"Period: {result.get('period', {}).get('start_date')} to {result.get('period', {}).get('end_date')}")
    print(f"Agents Involved: {result.get('research_agents_involved', 0)}")
    print(f"Sources Cited: {result.get('quality_metrics', {}).get('sources_cited', 0)}")
    print(f"Confidence Score: {result.get('quality_metrics', {}).get('confidence_score', 0)}")

    if result.get('status') == 'failed':
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()