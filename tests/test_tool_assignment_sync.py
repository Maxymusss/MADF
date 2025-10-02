"""
Test Tool Assignment Sync Between YAML Config and Agent Runtime

Verifies that tools defined in YAML configs are correctly loaded into agent._tools
"""

import pytest
from pathlib import Path
from src.agents.base_agent import BaseAgent
from src.core.agent_config import load_agent_config


class MockAgent(BaseAgent):
    """Mock agent for testing BaseAgent functionality"""

    def get_available_tools(self):
        return self._tools

    def process_task(self, task_description, context):
        return {"status": "complete"}


def test_orchestrator_tools_loaded_from_yaml():
    """Test that Orchestrator agent loads tools from YAML config"""
    agent = MockAgent("Orchestrator", "Test Role", agent_id="orchestrator")

    # Should have loaded tools from orchestrator_config.yaml
    assert agent._tools, "Agent should have tools loaded from config"

    # Check for expected tools from orchestrator_config.yaml
    tools = agent._tools
    print(f"Orchestrator tools loaded: {tools}")

    # Expected from YAML (approximate, based on config):
    # - github_client (from PyGithub via integrations.github_client)
    # - tavily_client (from tavily-python via integrations.tavily_client)
    # - github_mcp, tavily_mcp, filesystem_mcp

    assert any("github" in tool for tool in tools), "Should have GitHub tools"
    assert any("tavily" in tool for tool in tools), "Should have Tavily tools"


def test_analyst_tools_loaded_from_yaml():
    """Test that Analyst agent loads tools from YAML config"""
    agent = MockAgent("Analyst", "Test Role", agent_id="analyst")

    assert agent._tools, "Agent should have tools loaded from config"

    tools = agent._tools
    print(f"Analyst tools loaded: {tools}")

    # Expected from YAML:
    # - serena_mcp (direct MCP SDK)
    # - context7_mcp, sequential_thinking_mcp (MCP bridge)

    assert any("serena" in tool for tool in tools), "Should have Serena MCP"
    assert any("context7" in tool for tool in tools), "Should have Context7 MCP"


def test_tool_name_parsing():
    """Test _parse_tool_name handles various formats"""
    agent = MockAgent("Test", "Test Role")

    # Test "via" pattern
    assert agent._parse_tool_name("PyGithub (via integrations.github_client)") == "github_client"
    assert agent._parse_tool_name("tavily-python (via integrations.tavily_client)") == "tavily_client"

    # Test simple MCP pattern
    assert agent._parse_tool_name("serena_mcp (semantic code search, LSP-based)") == "serena_mcp"
    assert agent._parse_tool_name("github_mcp (repository operations)") == "github_mcp"

    # Test edge cases
    assert agent._parse_tool_name("context7_mcp (documentation)") == "context7_mcp"
    assert agent._parse_tool_name("") is None


def test_validate_tool_available():
    """Test validate_tool_available method"""
    agent = MockAgent("Orchestrator", "Test Role", agent_id="orchestrator")

    # Should have loaded tools from YAML
    if agent._tools:
        first_tool = agent._tools[0]
        assert agent.validate_tool_available(first_tool), f"Tool {first_tool} should be available"

    # Tool not in config should not be available
    assert not agent.validate_tool_available("nonexistent_tool")


def test_agent_without_config_has_empty_tools():
    """Test agent without config (no agent_id) has empty tools list"""
    agent = MockAgent("Test", "Test Role")  # No agent_id provided

    # Should not have loaded any tools
    assert agent._tools == [], "Agent without config should have empty tools list"


def test_all_agents_load_tools():
    """Test that all 5 agents successfully load tools from their configs"""
    agent_ids = ["orchestrator", "analyst", "knowledge", "developer", "validator"]

    for agent_id in agent_ids:
        agent = MockAgent(agent_id.capitalize(), "Test Role", agent_id=agent_id)

        assert agent.config is not None, f"{agent_id} should have config loaded"
        assert agent._tools, f"{agent_id} should have tools loaded from config"

        print(f"{agent_id} tools: {agent._tools}")


if __name__ == "__main__":
    # Run tests manually
    print("Testing tool assignment sync...\n")

    test_orchestrator_tools_loaded_from_yaml()
    print("✓ Orchestrator tools loaded\n")

    test_analyst_tools_loaded_from_yaml()
    print("✓ Analyst tools loaded\n")

    test_tool_name_parsing()
    print("✓ Tool name parsing works\n")

    test_validate_tool_available()
    print("✓ Tool validation works\n")

    test_agent_without_config_has_empty_tools()
    print("✓ Agent without config has empty tools\n")

    test_all_agents_load_tools()
    print("✓ All 5 agents load tools\n")

    print("All tests passed!")
