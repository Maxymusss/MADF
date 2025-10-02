"""
Agent Configuration Loader with Pydantic Validation

Loads YAML agent configurations and validates against Pydantic models.
Adapted from BMAD agent configuration patterns for LangGraph agents.

FIXES APPLIED:
- HIGH PRIORITY: Capability name uniqueness validation
- MEDIUM PRIORITY: Inquiry pattern question mark validation (warns if not ending with '?')
"""

import yaml
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class AgentPersona(BaseModel):
    """Agent persona definition following BMAD pattern"""
    role: str = Field(..., description="Expert role description")
    style: str = Field(..., description="Behavioral attributes and working style")
    identity: str = Field(..., description="Self-concept and identity")
    focus: str = Field(..., description="Primary objectives and focus areas")
    core_principles: List[str] = Field(..., description="Guiding principles for behavior")

    @field_validator('core_principles')
    @classmethod
    def validate_principles(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Agent must have at least one core principle")
        return v


class AgentCapability(BaseModel):
    """Agent capability definition with inquiry patterns"""
    name: str = Field(..., description="Capability identifier")
    description: str = Field(..., description="What this capability does")
    inquiry_patterns: List[str] = Field(
        default_factory=list,
        description="Questions to ask before executing"
    )
    when_to_use: str = Field(..., description="Guidance on when to use this capability")
    workflow: Optional[List[str]] = Field(
        default=None,
        description="Step-by-step workflow (optional, for TDD, etc.)"
    )

    @field_validator('inquiry_patterns')
    @classmethod
    def validate_inquiry_patterns(cls, v):
        """
        MEDIUM PRIORITY FIX: Validate inquiry patterns are questions

        Warns if patterns don't end with '?' (should be questions)
        This is a warning, not an error, since some patterns might be valid statements
        """
        if not v:
            return v

        for pattern in v:
            pattern_stripped = pattern.strip()
            if not pattern_stripped.endswith('?'):
                warnings.warn(
                    f"Inquiry pattern should be a question ending with '?': '{pattern}'",
                    UserWarning
                )
        return v


class StoryFilePermissions(BaseModel):
    """Story file section permissions"""
    allowed_sections: List[str] = Field(..., description="Sections agent can update")
    forbidden_sections: List[str] = Field(..., description="Sections agent cannot modify")

    @field_validator('allowed_sections', 'forbidden_sections')
    @classmethod
    def validate_sections(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Must specify at least one section")
        return v


class QualityGates(BaseModel):
    """QA gate governance configuration"""
    decisions: List[str] = Field(..., description="Valid gate decision types")
    traceability_format: str = Field(..., description="Format for requirements traceability")
    risk_assessment: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Risk assessment configuration"
    )

    @field_validator('decisions')
    @classmethod
    def validate_decisions(cls, v):
        valid_decisions = {"PASS", "CONCERNS", "FAIL", "WAIVED"}
        for decision in v:
            if decision not in valid_decisions:
                raise ValueError(f"Invalid gate decision: {decision}. Must be one of {valid_decisions}")
        return v


class TDDWorkflow(BaseModel):
    """TDD workflow configuration"""
    enforcement: str = Field(..., description="Enforcement level: strict or advisory")
    phases: List[Dict[str, str]] = Field(..., description="TDD phases definition")

    @field_validator('enforcement')
    @classmethod
    def validate_enforcement(cls, v):
        if v not in ["strict", "advisory"]:
            raise ValueError("Enforcement must be 'strict' or 'advisory'")
        return v


class BlockingCondition(BaseModel):
    """Blocking condition configuration"""
    condition: str = Field(..., description="Condition that triggers blocking")
    action: str = Field(..., description="Action to take when condition met")


class InteractionPatterns(BaseModel):
    """Agent interaction patterns"""
    numbered_options: Optional[bool] = Field(default=False, description="Use numbered options")
    clarify_before_delegate: Optional[bool] = Field(default=False, description="Clarify before delegating")
    planning_phase: Optional[bool] = Field(default=False, description="Run planning phase")
    curiosity_driven: Optional[bool] = Field(default=False, description="Ask 'why' questions")
    evidence_based: Optional[bool] = Field(default=False, description="Ground in data")
    facilitation_mode: Optional[bool] = Field(default=False, description="Act as thinking partner")
    holistic_thinking: Optional[bool] = Field(default=False, description="Consider system-wide impacts")
    progressive_complexity: Optional[bool] = Field(default=False, description="Start simple, scale up")
    decision_capture: Optional[bool] = Field(default=False, description="Record decisions")
    advisory_mode: Optional[bool] = Field(default=False, description="Provide recommendations")
    depth_as_needed: Optional[bool] = Field(default=False, description="Adjust detail by risk")
    educational: Optional[bool] = Field(default=False, description="Explain rationale")
    pragmatic: Optional[bool] = Field(default=False, description="Distinguish must-fix from nice-to-have")
    minimal_code: Optional[bool] = Field(default=False, description="Only create necessary files")
    fix_first: Optional[bool] = Field(default=False, description="Address root causes")


class AgentInfo(BaseModel):
    """Basic agent information"""
    name: str = Field(..., description="Agent name")
    id: str = Field(..., description="Agent identifier")
    title: str = Field(..., description="Agent title/role description")


class AgentTools(BaseModel):
    """Agent tool assignments"""
    direct_libraries: Optional[List[str]] = Field(
        default_factory=list,
        description="Direct Python library integrations"
    )
    direct_mcp_sdk: Optional[List[str]] = Field(
        default_factory=list,
        description="Direct MCP SDK integrations (stdio)"
    )
    mcp_bridge: Optional[List[str]] = Field(
        default_factory=list,
        description="Tools via mapping_mcp_bridge.js"
    )


class AgentConfig(BaseModel):
    """Complete agent configuration"""
    agent: AgentInfo = Field(..., description="Agent basic information")
    persona: AgentPersona = Field(..., description="Agent persona definition")
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")
    tools: AgentTools = Field(..., description="Tool assignments")
    interaction_patterns: Optional[InteractionPatterns] = Field(
        default=None,
        description="Interaction patterns"
    )
    story_file_permissions: Optional[StoryFilePermissions] = Field(
        default=None,
        description="Story file permissions (Developer/Validator only)"
    )
    quality_gates: Optional[QualityGates] = Field(
        default=None,
        description="QA gate configuration (Validator only)"
    )
    tdd_workflow: Optional[TDDWorkflow] = Field(
        default=None,
        description="TDD workflow configuration (Developer only)"
    )
    blocking_conditions: Optional[List[BlockingCondition]] = Field(
        default=None,
        description="Blocking conditions (Developer only)"
    )

    @field_validator('capabilities')
    @classmethod
    def validate_capabilities(cls, v):
        """
        HIGH PRIORITY FIX: Validate capability names are unique

        Ensures no duplicate capability names within an agent configuration
        """
        if not v or len(v) == 0:
            raise ValueError("Agent must have at least one capability")

        # Check for duplicate capability names
        capability_names = [cap.name for cap in v]
        if len(capability_names) != len(set(capability_names)):
            # Find duplicates for better error message
            seen = set()
            duplicates = set()
            for name in capability_names:
                if name in seen:
                    duplicates.add(name)
                seen.add(name)

            raise ValueError(
                f"Capability names must be unique. Duplicate names found: {', '.join(sorted(duplicates))}"
            )

        return v


class AgentConfigLoader:
    """Loads and validates agent configurations from YAML files"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize config loader

        Args:
            config_dir: Directory containing agent config YAML files
                       (defaults to project_root/config/agents)
        """
        if config_dir is None:
            # Default to config/agents relative to this file
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config" / "agents"

        self.config_dir = Path(config_dir)

        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")

    def load_agent_config(self, agent_id: str) -> AgentConfig:
        """
        Load and validate agent configuration

        Args:
            agent_id: Agent identifier (e.g., "orchestrator", "analyst")

        Returns:
            Validated AgentConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config validation fails
        """
        config_file = self.config_dir / f"{agent_id}_config.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"Agent config not found: {config_file}")

        # Load YAML
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # Validate with Pydantic
        try:
            config = AgentConfig(**config_data)
            return config
        except Exception as e:
            raise ValueError(f"Config validation failed for {agent_id}: {e}")

    def load_all_agent_configs(self) -> Dict[str, AgentConfig]:
        """
        Load all agent configurations from config directory

        Returns:
            Dict mapping agent_id to AgentConfig
        """
        configs = {}

        for config_file in self.config_dir.glob("*_config.yaml"):
            # Extract agent_id from filename (e.g., "orchestrator_config.yaml" -> "orchestrator")
            agent_id = config_file.stem.replace("_config", "")

            try:
                configs[agent_id] = self.load_agent_config(agent_id)
            except Exception as e:
                print(f"Warning: Failed to load config for {agent_id}: {e}")

        return configs

    def validate_config_file(self, config_file: Path) -> bool:
        """
        Validate a config file without loading it

        Args:
            config_file: Path to config file

        Returns:
            True if valid, False otherwise
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            AgentConfig(**config_data)
            return True
        except Exception:
            return False


# Convenience functions

def load_agent_config(agent_id: str, config_dir: Optional[Path] = None) -> AgentConfig:
    """
    Load agent configuration (convenience function)

    Args:
        agent_id: Agent identifier
        config_dir: Optional config directory

    Returns:
        AgentConfig instance
    """
    loader = AgentConfigLoader(config_dir)
    return loader.load_agent_config(agent_id)


def load_all_configs(config_dir: Optional[Path] = None) -> Dict[str, AgentConfig]:
    """
    Load all agent configurations (convenience function)

    Args:
        config_dir: Optional config directory

    Returns:
        Dict mapping agent_id to AgentConfig
    """
    loader = AgentConfigLoader(config_dir)
    return loader.load_all_agent_configs()
