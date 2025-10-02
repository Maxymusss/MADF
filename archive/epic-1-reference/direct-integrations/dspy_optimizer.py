"""
DSPy Optimizer Integration - Story 1.4 Task 2
Native DSPy framework for agent optimization and prompt tuning

Provides:
- Agent signature definitions
- Optimization workflow for prompts
- Training example generation from logs
- Performance metric tracking
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import dspy
from dspy.teleprompt import BootstrapFewShot
try:
    from dspy.teleprompt import MIPRO
except ImportError:
    # MIPRO not available in current DSPy version
    MIPRO = None
from dspy.evaluate import Evaluate

from .postgres_manager_sync import PostgresManager
from .pattern_extractor_sync import PatternExtractor
from .quick_logger import QuickLogger


# ============================================================================
# AGENT SIGNATURES
# ============================================================================

class PlanningSignature(dspy.Signature):
    """Planning Agent signature - converts user requirements to task plan"""

    user_requirement = dspy.InputField(desc="User's feature request or task description")
    existing_context = dspy.InputField(desc="Existing codebase context and constraints")

    task_plan = dspy.OutputField(desc="Structured task breakdown with subtasks and acceptance criteria")
    confidence = dspy.OutputField(desc="Confidence score (0.0-1.0) in plan quality")


class DevelopmentSignature(dspy.Signature):
    """Development Agent signature - implements code from task plan"""

    task_description = dspy.InputField(desc="Specific task to implement from plan")
    codebase_context = dspy.InputField(desc="Relevant existing code and patterns")
    technical_constraints = dspy.InputField(desc="Technology stack and integration requirements")

    implementation = dspy.OutputField(desc="Code implementation with file paths and changes")
    test_strategy = dspy.OutputField(desc="Testing approach for this implementation")
    confidence = dspy.OutputField(desc="Confidence score (0.0-1.0) in implementation quality")


class ResearchSignature(dspy.Signature):
    """Research Agent signature - gathers context and documentation"""

    research_query = dspy.InputField(desc="Question or topic to research")
    available_sources = dspy.InputField(desc="Available documentation sources and tools")

    findings = dspy.OutputField(desc="Concise research findings with sources")
    recommendations = dspy.OutputField(desc="Actionable recommendations based on findings")
    confidence = dspy.OutputField(desc="Confidence score (0.0-1.0) in research completeness")


class QASignature(dspy.Signature):
    """QA Agent signature - validates implementation quality"""

    implementation = dspy.InputField(desc="Code implementation to validate")
    acceptance_criteria = dspy.InputField(desc="Success criteria from plan")
    test_results = dspy.InputField(desc="Automated test execution results")

    validation_result = dspy.OutputField(desc="Pass/fail decision with detailed reasoning")
    issues_found = dspy.OutputField(desc="List of issues or concerns identified")
    confidence = dspy.OutputField(desc="Confidence score (0.0-1.0) in validation accuracy")


class PMSignature(dspy.Signature):
    """PM Agent signature - coordinates workflow and decisions"""

    current_state = dspy.InputField(desc="Current workflow state and agent outputs")
    blockers = dspy.InputField(desc="Any blockers or issues requiring decisions")

    next_action = dspy.OutputField(desc="Next agent to invoke and transition reason")
    priority_adjustment = dspy.OutputField(desc="Any priority or scope adjustments needed")
    confidence = dspy.OutputField(desc="Confidence score (0.0-1.0) in decision quality")


# ============================================================================
# MADF MODULES
# ============================================================================

class MADFPlanningModule(dspy.Module):
    """Planning agent module with ChainOfThought reasoning"""

    def __init__(self):
        super().__init__()
        self.plan = dspy.ChainOfThought(PlanningSignature)

    def forward(self, user_requirement: str, existing_context: str) -> dspy.Prediction:
        return self.plan(
            user_requirement=user_requirement,
            existing_context=existing_context
        )


class MADFDevelopmentModule(dspy.Module):
    """Development agent module with ChainOfThought reasoning"""

    def __init__(self):
        super().__init__()
        self.develop = dspy.ChainOfThought(DevelopmentSignature)

    def forward(
        self,
        task_description: str,
        codebase_context: str,
        technical_constraints: str
    ) -> dspy.Prediction:
        return self.develop(
            task_description=task_description,
            codebase_context=codebase_context,
            technical_constraints=technical_constraints
        )


class MADFResearchModule(dspy.Module):
    """Research agent module with ChainOfThought reasoning"""

    def __init__(self):
        super().__init__()
        self.research = dspy.ChainOfThought(ResearchSignature)

    def forward(self, research_query: str, available_sources: str) -> dspy.Prediction:
        return self.research(
            research_query=research_query,
            available_sources=available_sources
        )


class MADFQAModule(dspy.Module):
    """QA agent module with ChainOfThought reasoning"""

    def __init__(self):
        super().__init__()
        self.validate = dspy.ChainOfThought(QASignature)

    def forward(
        self,
        implementation: str,
        acceptance_criteria: str,
        test_results: str
    ) -> dspy.Prediction:
        return self.validate(
            implementation=implementation,
            acceptance_criteria=acceptance_criteria,
            test_results=test_results
        )


class MADFPMModule(dspy.Module):
    """PM agent module with ChainOfThought reasoning"""

    def __init__(self):
        super().__init__()
        self.coordinate = dspy.ChainOfThought(PMSignature)

    def forward(self, current_state: str, blockers: str = "") -> dspy.Prediction:
        return self.coordinate(
            current_state=current_state,
            blockers=blockers
        )


# ============================================================================
# OPTIMIZER
# ============================================================================

class MADFOptimizer:
    """
    DSPy optimizer for MADF agents

    Extracts training examples from execution logs
    Optimizes agent prompts using BootstrapFewShot or MIPRO
    Tracks performance improvements over time
    """

    def __init__(
        self,
        postgres_manager: Optional[PostgresManager] = None,
        model_name: str = "claude-3-5-sonnet-20241022"
    ):
        """
        Initialize MADF optimizer

        Args:
            postgres_manager: PostgresManager for log access
            model_name: LM model to use for optimization
        """
        self.pg = postgres_manager or PostgresManager()
        self.extractor = PatternExtractor(postgres_manager=self.pg)
        self.logger = QuickLogger()

        # Configure DSPy LM
        self.lm = dspy.Claude(model=model_name)
        dspy.settings.configure(lm=self.lm)

        # Agent modules
        self.modules = {
            "planning": MADFPlanningModule(),
            "development": MADFDevelopmentModule(),
            "research": MADFResearchModule(),
            "qa": MADFQAModule(),
            "pm": MADFPMModule()
        }

    def initialize(self):
        """Initialize Postgres connection"""
        self.pg.initialize()
        self.extractor.initialize()

    def extract_training_examples(
        self,
        agent_name: str,
        min_confidence: float = 0.85,
        limit: int = 50
    ) -> List[dspy.Example]:
        """
        Extract training examples from successful executions

        Args:
            agent_name: Agent to extract examples for
            min_confidence: Minimum confidence score for examples
            limit: Maximum examples to extract

        Returns:
            List of DSPy Example objects
        """
        # Get successful patterns with high confidence
        patterns = self.extractor.extract_training_examples(
            pattern_type="success",
            limit=limit
        )

        # Filter by agent and confidence
        agent_patterns = [
            p for p in patterns
            if p.get('agent_name') == agent_name
            and p.get('confidence_score', 0) >= min_confidence
        ]

        examples = []

        for pattern in agent_patterns:
            details = pattern.get('details', {})

            # Extract input/output pairs based on agent type
            if agent_name == "planning_agent":
                example = dspy.Example(
                    user_requirement=details.get('user_requirement', ''),
                    existing_context=details.get('context', ''),
                    task_plan=details.get('task_plan', ''),
                    confidence=pattern.get('confidence_score', 0.0)
                ).with_inputs('user_requirement', 'existing_context')

            elif agent_name == "dev_agent":
                example = dspy.Example(
                    task_description=details.get('task_description', ''),
                    codebase_context=details.get('codebase_context', ''),
                    technical_constraints=details.get('technical_constraints', ''),
                    implementation=details.get('implementation', ''),
                    test_strategy=details.get('test_strategy', ''),
                    confidence=pattern.get('confidence_score', 0.0)
                ).with_inputs('task_description', 'codebase_context', 'technical_constraints')

            elif agent_name == "research_agent":
                example = dspy.Example(
                    research_query=details.get('research_query', ''),
                    available_sources=details.get('available_sources', ''),
                    findings=details.get('findings', ''),
                    recommendations=details.get('recommendations', ''),
                    confidence=pattern.get('confidence_score', 0.0)
                ).with_inputs('research_query', 'available_sources')

            elif agent_name == "qa_agent":
                example = dspy.Example(
                    implementation=details.get('implementation', ''),
                    acceptance_criteria=details.get('acceptance_criteria', ''),
                    test_results=details.get('test_results', ''),
                    validation_result=details.get('validation_result', ''),
                    issues_found=details.get('issues_found', ''),
                    confidence=pattern.get('confidence_score', 0.0)
                ).with_inputs('implementation', 'acceptance_criteria', 'test_results')

            elif agent_name == "pm_agent":
                example = dspy.Example(
                    current_state=details.get('current_state', ''),
                    blockers=details.get('blockers', ''),
                    next_action=details.get('next_action', ''),
                    priority_adjustment=details.get('priority_adjustment', ''),
                    confidence=pattern.get('confidence_score', 0.0)
                ).with_inputs('current_state', 'blockers')

            else:
                continue

            examples.append(example)

        self.logger.log(
            event_type="agent_action",
            category="learning",
            agent_name="optimizer",
            details={
                "action": "extract_training_examples",
                "agent": agent_name,
                "examples_extracted": len(examples)
            }
        )

        return examples

    def optimize_agent(
        self,
        agent_name: str,
        optimizer_type: str = "bootstrap",
        max_bootstrapped_demos: int = 4,
        max_labeled_demos: int = 8
    ) -> Tuple[dspy.Module, Dict[str, Any]]:
        """
        Optimize agent module using training examples

        Args:
            agent_name: Agent to optimize
            optimizer_type: "bootstrap" or "mipro"
            max_bootstrapped_demos: Max bootstrap examples
            max_labeled_demos: Max labeled examples

        Returns:
            Tuple of (optimized_module, metrics)
        """
        # Map agent name to module key
        module_key = agent_name.replace("_agent", "")
        if module_key not in self.modules:
            raise ValueError(f"Unknown agent: {agent_name}")

        # Extract training examples
        examples = self.extract_training_examples(agent_name, limit=50)

        if len(examples) < 5:
            raise ValueError(f"Insufficient training examples for {agent_name}: {len(examples)}")

        # Split into train/validation
        train_size = int(len(examples) * 0.8)
        trainset = examples[:train_size]
        valset = examples[train_size:]

        # Get module to optimize
        module = self.modules[module_key]

        # Define metric (confidence score)
        def confidence_metric(example, prediction, trace=None):
            """Metric based on confidence score"""
            return float(getattr(prediction, 'confidence', 0.0))

        # Configure optimizer
        if optimizer_type == "bootstrap":
            optimizer = BootstrapFewShot(
                metric=confidence_metric,
                max_bootstrapped_demos=max_bootstrapped_demos,
                max_labeled_demos=max_labeled_demos
            )
        elif optimizer_type == "mipro":
            if MIPRO is None:
                raise ValueError("MIPRO optimizer not available in current DSPy version")
            optimizer = MIPRO(
                metric=confidence_metric,
                num_candidates=10,
                init_temperature=1.0
            )
        else:
            raise ValueError(f"Unknown optimizer type: {optimizer_type}")

        # Run optimization
        optimized_module = optimizer.compile(
            module,
            trainset=trainset,
            valset=valset
        )

        # Evaluate performance
        evaluator = Evaluate(
            devset=valset,
            metric=confidence_metric,
            display_progress=True
        )

        baseline_score = evaluator(module)
        optimized_score = evaluator(optimized_module)

        metrics = {
            "agent": agent_name,
            "optimizer": optimizer_type,
            "training_examples": len(trainset),
            "validation_examples": len(valset),
            "baseline_score": baseline_score,
            "optimized_score": optimized_score,
            "improvement": optimized_score - baseline_score
        }

        self.logger.log(
            event_type="decision",
            category="learning",
            agent_name="optimizer",
            success=True,
            confidence_score=optimized_score,
            details={
                "action": "optimize_agent",
                "metrics": metrics
            }
        )

        return optimized_module, metrics

    def save_optimized_module(
        self,
        module: dspy.Module,
        agent_name: str,
        output_dir: Path = Path("src/core/optimized_modules")
    ) -> Path:
        """
        Save optimized module to disk

        Args:
            module: Optimized DSPy module
            agent_name: Agent name for filename
            output_dir: Output directory

        Returns:
            Path to saved module
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        module_path = output_dir / f"{agent_name}_optimized.json"
        module.save(str(module_path))

        return module_path

    def close(self):
        """Close connections"""
        self.pg.close()
        self.extractor.close()


def main():
    """CLI entry point for DSPy optimization"""
    import argparse

    parser = argparse.ArgumentParser(description="MADF DSPy Optimizer")
    parser.add_argument(
        "agent",
        choices=["planning", "dev", "research", "qa", "pm"],
        help="Agent to optimize"
    )
    parser.add_argument(
        "--optimizer",
        choices=["bootstrap", "mipro"],
        default="bootstrap",
        help="Optimizer type"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("src/core/optimized_modules"),
        help="Output directory for optimized modules"
    )

    args = parser.parse_args()

    agent_name = f"{args.agent}_agent"

    optimizer = MADFOptimizer()
    optimizer.initialize()

    try:
        optimized_module, metrics = optimizer.optimize_agent(
            agent_name,
            optimizer_type=args.optimizer
        )

        print(f"\n[OK] Optimization complete for {agent_name}")
        print(f"  Baseline score: {metrics['baseline_score']:.3f}")
        print(f"  Optimized score: {metrics['optimized_score']:.3f}")
        print(f"  Improvement: {metrics['improvement']:.3f}")

        # Save optimized module
        module_path = optimizer.save_optimized_module(
            optimized_module,
            agent_name,
            args.output_dir
        )
        print(f"  Saved to: {module_path}")

    finally:
        optimizer.close()


if __name__ == "__main__":
    main()
