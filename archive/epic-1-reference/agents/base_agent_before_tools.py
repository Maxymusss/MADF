"""
Base Agent Class for MADF Specialized Agents

Provides common interface and functionality for all agent types.
Enhanced with BMAD patterns: persona structure, inquiry protocols, capabilities registry.

FIXES APPLIED:
- HIGH PRIORITY: Sophisticated keyword extraction via ContextKeywordExtractor
- MEDIUM PRIORITY: _match_capability() returns None if no confident match (no default fallback)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from ..core.agent_config import AgentConfig, AgentConfigLoader, AgentPersona, AgentCapability
    from ..core.context_keyword_extractor import ContextKeywordExtractor
except ImportError:
    from src.core.agent_config import AgentConfig, AgentConfigLoader, AgentPersona, AgentCapability
    from src.core.context_keyword_extractor import ContextKeywordExtractor


class BaseAgent(ABC):
    """
    Abstract base class for all MADF agents

    Enhanced with BMAD patterns:
    - Persona structure (role, style, identity, focus, core_principles)
    - Inquiry protocols (clarify_task before execution)
    - Capabilities registry (get_capabilities)
    """

    def __init__(
        self,
        name: str,
        role: str,
        agent_id: Optional[str] = None,
        config_dir: Optional[Path] = None
    ):
        """
        Initialize agent with optional YAML config loading

        Args:
            name: Agent name
            role: Agent role (legacy, overridden by persona if config loaded)
            agent_id: Agent ID for config loading (e.g., "orchestrator")
            config_dir: Optional config directory path
        """
        self.name = name
        self.role = role
        self._tools = []

        # BMAD enhancements
        self.agent_id = agent_id or name.lower()
        self.config: Optional[AgentConfig] = None
        self.persona: Optional[AgentPersona] = None
        self.capabilities: List[AgentCapability] = []

        # Load config if agent_id provided
        if agent_id:
            self._load_config(config_dir)

    def _load_config(self, config_dir: Optional[Path] = None):
        """
        Load agent configuration from YAML

        Args:
            config_dir: Optional config directory (defaults to project_root/config/agents)
        """
        try:
            loader = AgentConfigLoader(config_dir)
            self.config = loader.load_agent_config(self.agent_id)

            # Extract persona and capabilities
            self.persona = self.config.persona
            self.capabilities = self.config.capabilities

            # Update role from persona if loaded
            if self.persona:
                self.role = self.persona.role

        except Exception as e:
            print(f"Warning: Failed to load config for {self.agent_id}: {e}")
            print(f"Agent will operate without persona/capability configuration")

    def get_persona(self) -> Optional[AgentPersona]:
        """
        Get agent persona

        Returns:
            AgentPersona if config loaded, None otherwise
        """
        return self.persona

    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get agent capabilities as structured dict

        Returns:
            List of capability dicts with name, description, inquiry_patterns, when_to_use
        """
        if not self.capabilities:
            return []

        return [
            {
                "name": cap.name,
                "description": cap.description,
                "inquiry_patterns": cap.inquiry_patterns,
                "when_to_use": cap.when_to_use,
                "workflow": cap.workflow if cap.workflow else None
            }
            for cap in self.capabilities
        ]

    def clarify_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clarify task before execution using inquiry patterns

        This implements BMAD's inquiry/planning protocol:
        - Identify ambiguities in context
        - Ask questions based on capability inquiry_patterns
        - Return questions or confirm readiness to proceed

        Args:
            task: Task description
            context: Current task context

        Returns:
            Dict with:
                - clear: bool (True if ready to proceed, False if needs clarification)
                - questions: List[str] (questions needing answers)
                - capability: str (matched capability name)
                - alternatives: List[str] (alternative approaches if applicable)
        """
        # Match task to capability
        capability = self._match_capability(task)

        if not capability:
            return {
                "clear": False,
                "error": f"No matching capability found for task: {task}",
                "questions": [f"What should I do with this task: '{task}'?"],
                "available_capabilities": [cap.name for cap in self.capabilities]
            }

        # Check inquiry patterns against context
        questions = []
        for pattern in capability.inquiry_patterns:
            # Use sophisticated keyword matching
            if not self._has_context_for_pattern(pattern, context):
                questions.append(pattern)

        # Prepare alternatives if multiple capabilities could match
        alternatives = self._find_alternative_capabilities(task, capability)

        return {
            "clear": len(questions) == 0,
            "questions": questions,
            "capability": capability.name,
            "alternatives": alternatives if alternatives else None
        }

    def _match_capability(self, task: str) -> Optional[AgentCapability]:
        """
        Match task description to capability

        MEDIUM PRIORITY FIX: Return None if no confident match found (don't default to first capability)

        Args:
            task: Task description

        Returns:
            Matching AgentCapability or None if no confident match found
        """
        if not self.capabilities:
            return None

        task_lower = task.lower()

        # Try exact match first (capability name in task)
        for cap in self.capabilities:
            if cap.name.lower() in task_lower:
                return cap

        # Try description match (require at least 2 matching words for confidence)
        best_match = None
        best_match_count = 0

        for cap in self.capabilities:
            desc_words = set(cap.description.lower().split())
            task_words = set(task_lower.split())
            match_count = len(desc_words.intersection(task_words))

            if match_count > best_match_count:
                best_match_count = match_count
                best_match = cap

        # Return best match if at least 2 words matched
        if best_match_count >= 2:
            return best_match

        # No confident match found - return None (caller will handle)
        return None

    def _has_context_for_pattern(self, pattern: str, context: Dict[str, Any]) -> bool:
        """
        Check if context has information addressing inquiry pattern

        HIGH PRIORITY FIX: Use sophisticated keyword extraction instead of hardcoded checks

        Args:
            pattern: Inquiry pattern (question)
            context: Current context dict

        Returns:
            True if context addresses pattern, False otherwise
        """
        # Use ContextKeywordExtractor for sophisticated keyword matching
        return ContextKeywordExtractor.has_context_for_pattern(pattern, context)

    def _find_alternative_capabilities(
        self,
        task: str,
        current_capability: AgentCapability
    ) -> List[str]:
        """
        Find alternative capabilities that could handle this task

        Args:
            task: Task description
            current_capability: Currently matched capability

        Returns:
            List of alternative capability names
        """
        alternatives = []
        task_lower = task.lower()

        for cap in self.capabilities:
            if cap.name == current_capability.name:
                continue

            # Check if capability description matches task keywords
            desc_words = set(cap.description.lower().split())
            task_words = set(task_lower.split())
            match_count = len(desc_words.intersection(task_words))

            # Include as alternative if at least 1 word matches
            if match_count >= 1:
                alternatives.append(cap.name)

        return alternatives

    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """Return list of tools available to this agent"""
        pass

    @abstractmethod
    def process_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task and return results

        BMAD Enhancement: Implementations should call clarify_task() first
        and return {"status": "needs_clarification", "questions": [...]} if unclear
        """
        pass

    def add_tool(self, tool_name: str):
        """Add a tool to agent's available tools"""
        if tool_name not in self._tools:
            self._tools.append(tool_name)

    def remove_tool(self, tool_name: str):
        """Remove a tool from agent's available tools"""
        if tool_name in self._tools:
            self._tools.remove(tool_name)
