"""
Multi-Agent Development Framework (MADF) - LangGraph Implementation
Replaces the overengineered enterprise PRD with a focused LangGraph workflow
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Annotated
from typing_extensions import TypedDict
from datetime import datetime

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MADFState(TypedDict):
    """State schema for MADF workflow coordination"""
    # Core task information
    task: Dict[str, Any]              # Original task details
    task_id: str                      # Unique task identifier
    task_type: str                    # Classification (frontend/backend/qa/research/etc)

    # Workflow coordination
    agent_history: Annotated[List[Dict], add_messages]  # Agent handoff chain
    current_agent: str                # Currently active agent
    next_agent: Optional[str]         # Next agent in workflow

    # Results and progress
    results: Dict[str, Any]           # Accumulated results from each agent
    status: str                       # Current workflow status
    confidence_score: float           # Overall confidence in results

    # Error handling
    errors: List[Dict]                # Error tracking
    retry_count: int                  # Number of retries attempted

    # Context and metadata
    project_context: Dict[str, Any]   # Project-specific context (alphaseek, etc)
    created_at: str                   # Timestamp
    updated_at: str                   # Last update timestamp


class MADFWorkflow:
    """Main LangGraph workflow for multi-agent development coordination"""

    def __init__(self, config_path: str = ".claude"):
        self.config_path = config_path
        self.claude_model = None
        self.agent_configs = {}
        self.graph = None

        # Initialize components
        self._load_agent_configurations()
        self._initialize_claude_model()
        self._build_workflow_graph()

    def _load_agent_configurations(self):
        """Load existing agent configurations from .claude/agents/"""
        agents_dir = os.path.join(self.config_path, "agents")

        if not os.path.exists(agents_dir):
            logger.warning(f"Agents directory not found: {agents_dir}")
            return

        for filename in os.listdir(agents_dir):
            if filename.endswith('.json'):
                agent_path = os.path.join(agents_dir, filename)
                try:
                    with open(agent_path, 'r', encoding='utf-8') as f:
                        agent_config = json.load(f)
                        agent_name = filename.replace('.json', '').lower()
                        self.agent_configs[agent_name] = agent_config
                        logger.info(f"Loaded agent config: {agent_name}")
                except Exception as e:
                    logger.error(f"Failed to load agent config {filename}: {e}")

    def _initialize_claude_model(self):
        """Initialize Claude model for agent operations"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Get your API key from https://console.anthropic.com/settings/keys"
            )

        # Use Task Master configuration if available
        taskmaster_config_path = os.path.join(".taskmaster", "config.json")
        if os.path.exists(taskmaster_config_path):
            try:
                with open(taskmaster_config_path, 'r') as f:
                    taskmaster_config = json.load(f)
                    model_id = taskmaster_config.get("models", {}).get("main", {}).get("modelId", "claude-3-5-sonnet-latest")
            except Exception as e:
                logger.warning(f"Failed to load Task Master config: {e}")
                model_id = "claude-3-5-sonnet-latest"
        else:
            model_id = "claude-3-5-sonnet-latest"

        self.claude_model = init_chat_model(f"anthropic:{model_id}")
        logger.info(f"Initialized Claude model: {model_id}")

    def _build_workflow_graph(self):
        """Build the LangGraph workflow with specialized agent nodes"""
        graph_builder = StateGraph(MADFState)

        # Add agent nodes
        graph_builder.add_node("task_intake", self._task_intake_node)
        graph_builder.add_node("research", self._research_agent_node)
        graph_builder.add_node("implementation", self._implementation_agent_node)
        graph_builder.add_node("quality_assurance", self._qa_agent_node)
        graph_builder.add_node("completion", self._completion_node)

        # Define workflow edges
        graph_builder.add_edge(START, "task_intake")

        # Conditional routing from task_intake
        graph_builder.add_conditional_edges(
            "task_intake",
            self._route_after_intake,
            {
                "research": "research",
                "implementation": "implementation",
                "qa": "quality_assurance",
                "end": END
            }
        )

        # Research -> Implementation
        graph_builder.add_edge("research", "implementation")

        # Implementation -> Quality Assurance
        graph_builder.add_edge("implementation", "quality_assurance")

        # Quality Assurance -> Completion
        graph_builder.add_edge("quality_assurance", "completion")

        # Completion -> End
        graph_builder.add_edge("completion", END)

        # Compile the graph
        self.graph = graph_builder.compile()
        logger.info("LangGraph workflow compiled successfully")

    def _task_intake_node(self, state: MADFState) -> MADFState:
        """Classify and route incoming tasks"""
        logger.info(f"Processing task intake for task: {state.get('task_id', 'unknown')}")

        task = state.get("task", {})
        task_description = task.get("description", "")

        # Task classification logic
        task_type = self._classify_task(task_description)

        # Initialize workflow state
        current_time = datetime.now().isoformat()

        updated_state = {
            **state,
            "task_type": task_type,
            "current_agent": "task_intake",
            "status": "classified",
            "confidence_score": 0.7,  # Initial confidence
            "errors": [],
            "retry_count": 0,
            "updated_at": current_time,
            "agent_history": [
                {
                    "agent": "task_intake",
                    "action": "classified_task",
                    "task_type": task_type,
                    "timestamp": current_time
                }
            ]
        }

        logger.info(f"Task classified as: {task_type}")
        return updated_state

    def _research_agent_node(self, state: MADFState) -> MADFState:
        """Research agent for investigation and analysis"""
        logger.info("Executing research agent")

        # Get research agent configuration
        research_config = self.agent_configs.get("researchagent", {})

        # Build specialized prompt for research
        task_description = state.get("task", {}).get("description", "")

        prompt = self._build_agent_prompt(
            agent_config=research_config,
            task_description=task_description,
            agent_role="research"
        )

        try:
            # Make API call to Claude
            response = self.claude_model.invoke([{"role": "user", "content": prompt}])

            # Process response
            research_results = {
                "findings": response.content,
                "confidence": 0.8,
                "sources_analyzed": [],  # Could be populated with actual sources
                "recommendations": []
            }

            # Update state
            current_time = datetime.now().isoformat()
            updated_state = {
                **state,
                "current_agent": "research",
                "next_agent": "implementation",
                "results": {
                    **state.get("results", {}),
                    "research": research_results
                },
                "confidence_score": max(state.get("confidence_score", 0), 0.8),
                "updated_at": current_time,
                "agent_history": state.get("agent_history", []) + [
                    {
                        "agent": "research",
                        "action": "completed_research",
                        "timestamp": current_time,
                        "confidence": 0.8
                    }
                ]
            }

            logger.info("Research agent completed successfully")
            return updated_state

        except Exception as e:
            logger.error(f"Research agent failed: {e}")
            return self._handle_agent_error(state, "research", str(e))

    def _implementation_agent_node(self, state: MADFState) -> MADFState:
        """Implementation agent for code development"""
        logger.info("Executing implementation agent")

        # Get PM agent configuration (closest to implementation)
        pm_config = self.agent_configs.get("pmagent", {})

        # Build implementation prompt
        task_description = state.get("task", {}).get("description", "")
        research_results = state.get("results", {}).get("research", {})

        prompt = self._build_agent_prompt(
            agent_config=pm_config,
            task_description=task_description,
            agent_role="implementation",
            context=research_results
        )

        try:
            # Make API call to Claude
            response = self.claude_model.invoke([{"role": "user", "content": prompt}])

            # Process response
            implementation_results = {
                "code_changes": response.content,
                "confidence": 0.85,
                "files_modified": [],  # Could be parsed from response
                "tests_required": True
            }

            # Update state
            current_time = datetime.now().isoformat()
            updated_state = {
                **state,
                "current_agent": "implementation",
                "next_agent": "quality_assurance",
                "results": {
                    **state.get("results", {}),
                    "implementation": implementation_results
                },
                "confidence_score": max(state.get("confidence_score", 0), 0.85),
                "updated_at": current_time,
                "agent_history": state.get("agent_history", []) + [
                    {
                        "agent": "implementation",
                        "action": "completed_implementation",
                        "timestamp": current_time,
                        "confidence": 0.85
                    }
                ]
            }

            logger.info("Implementation agent completed successfully")
            return updated_state

        except Exception as e:
            logger.error(f"Implementation agent failed: {e}")
            return self._handle_agent_error(state, "implementation", str(e))

    def _qa_agent_node(self, state: MADFState) -> MADFState:
        """Quality Assurance agent for validation and testing"""
        logger.info("Executing QA agent")

        # Get code reviewer configuration
        qa_config = self.agent_configs.get("code-reviewer", {})

        # Build QA prompt
        task_description = state.get("task", {}).get("description", "")
        implementation_results = state.get("results", {}).get("implementation", {})

        prompt = self._build_agent_prompt(
            agent_config=qa_config,
            task_description=task_description,
            agent_role="quality_assurance",
            context=implementation_results
        )

        try:
            # Make API call to Claude
            response = self.claude_model.invoke([{"role": "user", "content": prompt}])

            # Process response
            qa_results = {
                "review_summary": response.content,
                "confidence": 0.9,
                "issues_found": [],  # Could be parsed from response
                "approval_status": "approved"  # Could be determined from response
            }

            # Update state
            current_time = datetime.now().isoformat()
            updated_state = {
                **state,
                "current_agent": "quality_assurance",
                "next_agent": "completion",
                "status": "qa_complete",
                "results": {
                    **state.get("results", {}),
                    "qa": qa_results
                },
                "confidence_score": max(state.get("confidence_score", 0), 0.9),
                "updated_at": current_time,
                "agent_history": state.get("agent_history", []) + [
                    {
                        "agent": "quality_assurance",
                        "action": "completed_qa",
                        "timestamp": current_time,
                        "confidence": 0.9
                    }
                ]
            }

            logger.info("QA agent completed successfully")
            return updated_state

        except Exception as e:
            logger.error(f"QA agent failed: {e}")
            return self._handle_agent_error(state, "quality_assurance", str(e))

    def _completion_node(self, state: MADFState) -> MADFState:
        """Final completion node for workflow finalization"""
        logger.info("Executing completion node")

        current_time = datetime.now().isoformat()

        # Calculate final metrics
        final_confidence = state.get("confidence_score", 0)
        total_agents = len(state.get("agent_history", []))

        completion_summary = {
            "workflow_completed": True,
            "total_agents_involved": total_agents,
            "final_confidence": final_confidence,
            "completion_time": current_time,
            "success": len(state.get("errors", [])) == 0
        }

        updated_state = {
            **state,
            "current_agent": "completion",
            "status": "completed",
            "results": {
                **state.get("results", {}),
                "completion": completion_summary
            },
            "updated_at": current_time,
            "agent_history": state.get("agent_history", []) + [
                {
                    "agent": "completion",
                    "action": "workflow_completed",
                    "timestamp": current_time,
                    "final_confidence": final_confidence
                }
            ]
        }

        logger.info(f"Workflow completed with confidence: {final_confidence}")
        return updated_state

    def _classify_task(self, task_description: str) -> str:
        """Classify task type based on description"""
        task_lower = task_description.lower()

        # Simple classification logic
        if any(keyword in task_lower for keyword in ["research", "analyze", "investigate", "study"]):
            return "research"
        elif any(keyword in task_lower for keyword in ["test", "qa", "quality", "review", "validate"]):
            return "qa"
        elif any(keyword in task_lower for keyword in ["implement", "code", "develop", "build", "create"]):
            return "implementation"
        else:
            return "general"

    def _route_after_intake(self, state: MADFState) -> str:
        """Route to appropriate agent after task intake"""
        task_type = state.get("task_type", "general")

        # Simple routing logic
        if task_type == "research":
            return "research"
        elif task_type == "qa":
            return "quality_assurance"
        elif task_type == "implementation":
            return "research"  # Start with research for implementation tasks
        else:
            return "research"  # Default to research for general tasks

    def _build_agent_prompt(self, agent_config: Dict, task_description: str,
                           agent_role: str, context: Optional[Dict] = None) -> str:
        """Build specialized prompt for agent based on configuration"""

        agent_name = agent_config.get("name", "Agent")
        agent_description = agent_config.get("description", "")
        capabilities = agent_config.get("capabilities", [])

        prompt_parts = [
            f"You are {agent_name}, specialized in {agent_role}.",
            f"Description: {agent_description}",
            f"Your capabilities include: {', '.join(capabilities)}",
            "",
            f"Task to complete: {task_description}",
        ]

        if context:
            prompt_parts.extend([
                "",
                "Previous context from other agents:",
                json.dumps(context, indent=2)
            ])

        prompt_parts.extend([
            "",
            f"Please provide your {agent_role} analysis and recommendations.",
            "Focus on actionable insights and specific next steps."
        ])

        return "\n".join(prompt_parts)

    def _handle_agent_error(self, state: MADFState, agent_name: str, error_message: str) -> MADFState:
        """Handle agent execution errors"""
        current_time = datetime.now().isoformat()

        error_info = {
            "agent": agent_name,
            "error": error_message,
            "timestamp": current_time,
            "retry_count": state.get("retry_count", 0) + 1
        }

        updated_state = {
            **state,
            "status": "error",
            "errors": state.get("errors", []) + [error_info],
            "retry_count": state.get("retry_count", 0) + 1,
            "updated_at": current_time
        }

        return updated_state

    def execute_task(self, task: Dict[str, Any], project_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a task through the multi-agent workflow"""

        # Generate unique task ID
        task_id = f"task_{int(datetime.now().timestamp())}"

        # Initialize state
        initial_state = MADFState(
            task=task,
            task_id=task_id,
            task_type="",
            agent_history=[],
            current_agent="",
            next_agent=None,
            results={},
            status="initialized",
            confidence_score=0.0,
            errors=[],
            retry_count=0,
            project_context=project_context or {},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        logger.info(f"Starting workflow execution for task: {task_id}")

        try:
            # Execute the workflow
            final_state = self.graph.invoke(initial_state)

            logger.info(f"Workflow completed for task: {task_id}")
            return final_state

        except Exception as e:
            logger.error(f"Workflow execution failed for task {task_id}: {e}")
            return {
                **initial_state,
                "status": "failed",
                "errors": [{"error": str(e), "timestamp": datetime.now().isoformat()}]
            }


def create_madf_workflow() -> MADFWorkflow:
    """Factory function to create MADF workflow instance"""
    return MADFWorkflow()


if __name__ == "__main__":
    # Example usage
    try:
        workflow = create_madf_workflow()

        # Example task
        sample_task = {
            "description": "Implement user authentication system for alphaseek project",
            "priority": "high",
            "project": "alphaseek"
        }

        # Execute workflow
        result = workflow.execute_task(
            task=sample_task,
            project_context={"project_name": "alphaseek", "stage": "growth"}
        )

        print("Workflow Results:")
        print(f"Status: {result.get('status')}")
        print(f"Confidence: {result.get('confidence_score')}")
        print(f"Agents involved: {len(result.get('agent_history', []))}")

        if result.get('errors'):
            print(f"Errors: {result.get('errors')}")

    except Exception as e:
        print(f"Failed to execute workflow: {e}")