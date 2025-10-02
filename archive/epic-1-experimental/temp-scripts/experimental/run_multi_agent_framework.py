"""
Multi-Agent Financial Research Framework - Main Orchestrator
Demonstrates the complete workflow: Product Manager → Research Agents → Validator → Final Report
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

# Import our agent classes
from agents.product_manager_agent import ProductManagerAgent
from agents.research_agent import ResearchAgent
from agents.validator_agent import ValidatorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiAgentFramework:
    """
    Main orchestrator for the multi-agent financial research framework
    Demonstrates the hybrid BMAD + MCP-use architecture
    """

    def __init__(self, workspace_dir: str = "agent_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)

        # Initialize Product Manager Agent
        self.product_manager = ProductManagerAgent(workspace_dir)

        logger.info("Multi-Agent Framework initialized")

    async def run_fx_rates_research_workflow(self, regions: list = None, markets: list = None) -> dict:
        """
        Execute the complete FX/rates research workflow
        """
        if regions is None:
            regions = ["Asia", "G10"]
        if markets is None:
            markets = ["currencies", "interest_rates"]

        logger.info("=== Starting Multi-Agent FX/Rates Research Workflow ===")

        try:
            # Step 1: Product Manager creates task and deploys agents
            logger.info("Step 1: Product Manager creating research task...")
            task_id = f"fx_rates_{int(datetime.now().timestamp())}"

            # Create research task
            task_spec = self.product_manager.create_research_task(task_id, regions, markets)
            logger.info(f"Created task: {task_id} for period {task_spec['timeframe']['description']}")

            # Deploy research agents with different strategies
            logger.info("Step 2: Deploying research agents...")
            research_agent_ids = self.product_manager.deploy_research_agents(task_id, num_agents=2)

            # Deploy validator agent
            logger.info("Step 3: Deploying validator agent...")
            validator_id = self.product_manager.deploy_validator_agent(task_id, research_agent_ids)

            # Step 2: Execute research agents in parallel
            logger.info("Step 4: Executing research agents...")
            research_tasks = []

            for agent_id in research_agent_ids:
                research_agent = ResearchAgent(agent_id, str(self.workspace_dir))
                research_tasks.append(research_agent.execute_research_task())

            # Wait for research agents to complete
            research_results = await asyncio.gather(*research_tasks, return_exceptions=True)

            # Check research results
            successful_research = {}
            for i, result in enumerate(research_results):
                agent_id = research_agent_ids[i]
                if isinstance(result, Exception):
                    logger.error(f"Research agent {agent_id} failed: {result}")
                else:
                    successful_research[agent_id] = result
                    logger.info(f"Research agent {agent_id} completed successfully")

            if not successful_research:
                raise Exception("All research agents failed")

            # Step 3: Execute validator agent
            logger.info("Step 5: Executing validator agent...")
            validator_agent = ValidatorAgent(validator_id, str(self.workspace_dir))
            validation_result = await validator_agent.execute_validation_task()

            if validation_result.get("status") == "failed":
                logger.warning(f"Validation failed: {validation_result.get('error')}")
            else:
                logger.info("Validation completed successfully")

            # Step 4: Product Manager compiles final summary
            logger.info("Step 6: Compiling final summary...")
            final_summary = self.product_manager.compile_final_summary(
                task_id, successful_research, validation_result
            )

            # Step 5: Generate human-readable report
            logger.info("Step 7: Generating human-readable report...")
            readable_report = self.generate_readable_report(final_summary)

            logger.info("=== Multi-Agent Workflow Completed Successfully ===")

            return {
                "status": "completed",
                "task_id": task_id,
                "final_summary": final_summary,
                "readable_report": readable_report,
                "workflow_metrics": {
                    "research_agents_deployed": len(research_agent_ids),
                    "successful_research_agents": len(successful_research),
                    "validation_performed": validation_result.get("status") == "completed",
                    "total_sources": final_summary.get("quality_metrics", {}).get("sources_cited", 0),
                    "confidence_score": final_summary.get("quality_metrics", {}).get("confidence_score", 0)
                }
            }

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def generate_readable_report(self, final_summary: dict) -> str:
        """
        Generate a human-readable report from the final summary
        """
        period = final_summary.get("period", {})
        content = final_summary.get("content", {})
        quality_metrics = final_summary.get("quality_metrics", {})

        report_lines = [
            "=" * 60,
            "FX & INTEREST RATES MARKET SUMMARY",
            "=" * 60,
            "",
            f"Period: {period.get('start_date', 'Unknown')} to {period.get('end_date', 'Unknown')}",
            f"Regions: Asia, G10",
            f"Markets: Currencies, Interest Rates",
            "",
            "QUALITY METRICS:",
            f"• Sources Cited: {quality_metrics.get('sources_cited', 0)}",
            f"• Cross-References: {quality_metrics.get('cross_references', 0)}",
            f"• Confidence Score: {quality_metrics.get('confidence_score', 0):.2f}",
            f"• Timing Accuracy: {quality_metrics.get('timing_accuracy', 'Unknown')}",
            "",
            "KEY FINDINGS:",
            ""
        ]

        # Add key events
        key_events = content.get("key_events", [])
        if key_events:
            report_lines.append("KEY EVENTS:")
            for i, event in enumerate(key_events[:5], 1):  # Top 5 events
                report_lines.append(f"{i}. {event}")
            report_lines.append("")

        # Add currency movements
        currency_movements = content.get("currency_movements", [])
        if currency_movements:
            report_lines.append("CURRENCY MOVEMENTS:")
            for i, movement in enumerate(currency_movements[:5], 1):  # Top 5 movements
                report_lines.append(f"{i}. {movement}")
            report_lines.append("")

        # Add interest rate changes
        rate_changes = content.get("interest_rate_changes", [])
        if rate_changes:
            report_lines.append("INTEREST RATE CHANGES:")
            for i, change in enumerate(rate_changes[:3], 1):  # Top 3 changes
                report_lines.append(f"{i}. {change}")
            report_lines.append("")

        # Add central bank actions
        cb_actions = content.get("central_bank_actions", [])
        if cb_actions:
            report_lines.append("CENTRAL BANK ACTIONS:")
            for i, action in enumerate(cb_actions[:3], 1):  # Top 3 actions
                report_lines.append(f"{i}. {action}")
            report_lines.append("")

        # Add validation summary if available
        validation_data = final_summary.get("validation_data", {})
        if validation_data and validation_data.get("status") == "completed":
            validation_summary = validation_data.get("validation_summary", {})
            report_lines.extend([
                "VALIDATION RESULTS:",
                f"• Claims Verified: {validation_summary.get('claims_verified', 0)}",
                f"• Conflicts Detected: {validation_summary.get('conflicts_detected', 0)}",
                f"• Verification Rate: {validation_summary.get('verification_rate', 0):.1%}",
                f"• Overall Reliability: {validation_data.get('quality_assessment', {}).get('overall_reliability', 'Unknown')}",
                ""
            ])

        report_lines.extend([
            "=" * 60,
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Framework: Multi-Agent Financial Research (MADF)",
            "=" * 60
        ])

        return "\n".join(report_lines)

    def get_framework_status(self) -> dict:
        """
        Get current status of the framework and all agents
        """
        workspace_status = {
            "workspace_dir": str(self.workspace_dir),
            "directories": {
                "tasks": len(list((self.workspace_dir / "tasks").glob("*.json"))) if (self.workspace_dir / "tasks").exists() else 0,
                "results": len(list((self.workspace_dir / "results").glob("*.json"))) if (self.workspace_dir / "results").exists() else 0,
                "logs": len(list((self.workspace_dir / "logs").glob("*.json"))) if (self.workspace_dir / "logs").exists() else 0
            },
            "framework_ready": True,
            "mcp_use_available": True,  # Would check actual MCP-use availability in production
            "timestamp": datetime.now().isoformat()
        }

        return workspace_status


async def main():
    """
    Main function to demonstrate the multi-agent framework
    """
    print("Initializing Multi-Agent Financial Research Framework...")

    # Initialize framework
    framework = MultiAgentFramework()

    # Check framework status
    status = framework.get_framework_status()
    print(f"Framework Status: {'Ready' if status['framework_ready'] else 'Not Ready'}")
    print(f"Workspace: {status['workspace_dir']}")

    # Run FX/rates research workflow
    print("\nExecuting FX/Rates Research Workflow...")
    workflow_result = await framework.run_fx_rates_research_workflow()

    if workflow_result["status"] == "completed":
        print("\n" + "="*60)
        print("WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*60)

        # Print workflow metrics
        metrics = workflow_result["workflow_metrics"]
        print(f"Research Agents: {metrics['research_agents_deployed']}")
        print(f"Successful Agents: {metrics['successful_research_agents']}")
        print(f"Validation: {'✓' if metrics['validation_performed'] else '✗'}")
        print(f"Sources Found: {metrics['total_sources']}")
        print(f"Confidence: {metrics['confidence_score']:.2f}")

        # Print readable report
        print("\n" + workflow_result["readable_report"])

    else:
        print(f"\nWorkflow Failed: {workflow_result.get('error', 'Unknown error')}")

    print("\nFramework demonstration completed.")


if __name__ == "__main__":
    asyncio.run(main())