"""
Integration tests for Story 1.7 - BMAD agent integration
Verifies that all agents load YAML configs and BMAD patterns correctly
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.orchestrator_agent import OrchestratorAgent
from agents.analyst_agent import AnalystAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.developer_agent import DeveloperAgent
from agents.validator_agent import ValidatorAgent


class TestYAMLConfigLoading:
    """Test that agents load YAML configurations correctly"""

    def test_orchestrator_loads_config(self):
        """Orchestrator should load persona and tools from YAML"""
        agent = OrchestratorAgent()

        # Verify persona loaded
        assert agent.persona is not None, "Orchestrator should have persona loaded"
        assert agent.persona.role == "Workflow Coordinator & Product Planning Specialist"
        assert len(agent.persona.core_principles) > 0

        # Verify capabilities loaded
        assert len(agent.capabilities) > 0, "Orchestrator should have capabilities"
        capability_names = [cap.name for cap in agent.capabilities]
        assert "create_prd" in capability_names
        assert "decompose_epic" in capability_names

        # Verify tools loaded from YAML (not hardcoded)
        assert len(agent._tools) > 0, "Orchestrator should have tools loaded"
        assert "github_client" in agent._tools
        assert "tavily_client" in agent._tools

    def test_analyst_loads_config(self):
        """Analyst should load persona and tools from YAML"""
        agent = AnalystAgent()

        # Verify persona loaded
        assert agent.persona is not None, "Analyst should have persona loaded"
        assert "Analyst" in agent.persona.role

        # Verify capabilities loaded
        assert len(agent.capabilities) > 0, "Analyst should have capabilities"
        capability_names = [cap.name for cap in agent.capabilities]
        assert "elicit_requirements" in capability_names
        assert "analyze_codebase" in capability_names

        # Verify tools loaded from YAML
        assert len(agent._tools) > 0, "Analyst should have tools loaded"
        assert "serena_mcp" in agent._tools
        assert "context7_mcp" in agent._tools

    def test_knowledge_loads_config(self):
        """Knowledge should load persona and tools from YAML"""
        agent = KnowledgeAgent()

        # Verify persona loaded
        assert agent.persona is not None, "Knowledge should have persona loaded"
        assert "Knowledge" in agent.persona.role

        # Verify capabilities loaded
        assert len(agent.capabilities) > 0, "Knowledge should have capabilities"
        capability_names = [cap.name for cap in agent.capabilities]
        # Check for any knowledge-related capability
        has_knowledge_capability = any("knowledge" in name.lower() or "store" in name.lower() or "search" in name.lower() for name in capability_names)
        assert has_knowledge_capability, f"Should have knowledge capability, got: {capability_names}"

        # Verify tools loaded from YAML
        assert len(agent._tools) > 0, "Knowledge should have tools loaded"

    def test_developer_loads_config(self):
        """Developer should load persona and tools from YAML"""
        agent = DeveloperAgent()

        # Verify persona loaded
        assert agent.persona is not None, "Developer should have persona loaded"
        assert "Developer" in agent.persona.role or "Implementation" in agent.persona.role

        # Verify capabilities loaded
        assert len(agent.capabilities) > 0, "Developer should have capabilities"

        # Verify tools loaded from YAML
        assert len(agent._tools) > 0, "Developer should have tools loaded"

    def test_validator_loads_config(self):
        """Validator should load persona and tools from YAML"""
        agent = ValidatorAgent()

        # Verify persona loaded
        assert agent.persona is not None, "Validator should have persona loaded"
        assert "Validator" in agent.persona.role or "Quality" in agent.persona.role

        # Verify capabilities loaded
        assert len(agent.capabilities) > 0, "Validator should have capabilities"

        # Verify tools loaded from YAML
        assert len(agent._tools) > 0, "Validator should have tools loaded"


class TestInquiryProtocols:
    """Test that agents implement BMAD inquiry protocols"""

    def test_orchestrator_clarify_task(self):
        """Orchestrator should use inquiry patterns to clarify tasks"""
        agent = OrchestratorAgent()

        # Test with task matching "create_prd" capability
        result = agent.clarify_task(
            task="create_prd for new feature",
            context={}
        )

        # Should identify missing context
        assert result.get("clear") == False, "Should detect missing context"
        assert len(result.get("questions", [])) > 0, "Should ask clarifying questions"
        # Capability should be matched when name is in task
        if result.get("capability"):
            assert result.get("capability") == "create_prd"

        # Test with complete context
        result = agent.clarify_task(
            task="create_prd for new feature",
            context={
                "user_problem": "Users need to export data",
                "features": ["CSV export", "JSON export"],
                "target_users": "Data analysts",
                "success_metrics": "50% adoption in 3 months"
            }
        )

        # Should be clear with complete context
        assert result.get("clear") == True, "Should be clear with complete context"

    def test_analyst_clarify_task(self):
        """Analyst should use inquiry patterns to clarify tasks"""
        agent = AnalystAgent()

        # Test with task matching "elicit_requirements" capability
        result = agent.clarify_task(
            task="elicit requirements for feature",
            context={}
        )

        # Should ask questions
        assert result.get("clear") == False, "Should detect missing context"
        assert len(result.get("questions", [])) > 0, "Should ask clarifying questions"

    def test_no_matching_capability(self):
        """Agents should handle tasks with no matching capability"""
        agent = OrchestratorAgent()

        result = agent.clarify_task(
            task="do something completely unrelated",
            context={}
        )

        # Should indicate no matching capability
        assert "error" in result or result.get("clear") == False
        assert "available_capabilities" in result or "No matching capability" in result.get("error", "")


class TestCapabilities:
    """Test that capabilities are properly structured"""

    def test_orchestrator_capabilities_structure(self):
        """Orchestrator capabilities should have required fields"""
        agent = OrchestratorAgent()

        for cap in agent.capabilities:
            assert cap.name, "Capability must have name"
            assert cap.description, "Capability must have description"
            assert len(cap.inquiry_patterns) > 0, "Capability must have inquiry patterns"
            # All inquiry patterns should be questions
            for pattern in cap.inquiry_patterns:
                # Allow patterns with options like "(option1/option2)"
                base_pattern = pattern.split('(')[0].strip()
                if base_pattern:
                    assert base_pattern.endswith('?'), f"Inquiry pattern should be question: {pattern}"

    def test_all_agents_have_capabilities(self):
        """All agents should have at least one capability"""
        agents = [
            OrchestratorAgent(),
            AnalystAgent(),
            KnowledgeAgent(),
            DeveloperAgent(),
            ValidatorAgent()
        ]

        for agent in agents:
            assert len(agent.capabilities) > 0, f"{agent.name} should have capabilities"

    def test_capability_uniqueness(self):
        """Each agent should have unique capability names"""
        agent = OrchestratorAgent()

        capability_names = [cap.name for cap in agent.capabilities]
        assert len(capability_names) == len(set(capability_names)), "Capability names must be unique"


class TestToolAssignment:
    """Test that tools are correctly assigned from YAML"""

    def test_orchestrator_tools_match_yaml(self):
        """Orchestrator tools should match YAML config"""
        agent = OrchestratorAgent()

        # Expected tools from orchestrator_config.yaml
        expected_tools = ["github_client", "tavily_client", "github_mcp", "tavily_mcp", "filesystem_mcp"]

        for expected_tool in expected_tools:
            assert expected_tool in agent._tools, f"{expected_tool} should be in Orchestrator tools"

    def test_analyst_tools_match_yaml(self):
        """Analyst tools should match YAML config"""
        agent = AnalystAgent()

        # Expected tools from analyst_config.yaml
        expected_tools = ["serena_mcp", "context7_mcp", "sequential_thinking_mcp"]

        for expected_tool in expected_tools:
            assert expected_tool in agent._tools, f"{expected_tool} should be in Analyst tools"

    def test_validate_tool_available(self):
        """Test BaseAgent.validate_tool_available() method"""
        agent = OrchestratorAgent()

        # Should validate tools loaded from YAML
        assert agent.validate_tool_available("github_client"), "Should validate github_client"
        assert agent.validate_tool_available("tavily_client"), "Should validate tavily_client"
        assert not agent.validate_tool_available("nonexistent_tool"), "Should reject nonexistent tool"


class TestPersonaStructure:
    """Test that persona structure is correctly loaded"""

    def test_orchestrator_persona_fields(self):
        """Orchestrator persona should have all required fields"""
        agent = OrchestratorAgent()

        assert agent.persona.role, "Persona must have role"
        assert agent.persona.style, "Persona must have style"
        assert agent.persona.identity, "Persona must have identity"
        assert agent.persona.focus, "Persona must have focus"
        assert len(agent.persona.core_principles) > 0, "Persona must have core principles"

    def test_analyst_persona_fields(self):
        """Analyst persona should have all required fields"""
        agent = AnalystAgent()

        assert agent.persona.role, "Persona must have role"
        assert agent.persona.core_principles, "Persona must have core principles"

        # Analyst should have "Numbered Options Protocol" principle
        principles_text = " ".join(agent.persona.core_principles)
        assert "numbered" in principles_text.lower() or "options" in principles_text.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
