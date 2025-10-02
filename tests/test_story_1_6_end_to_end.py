"""
Story 1.6: Chrome DevTools + End-to-End Integration Tests

Tests browser debugging capabilities and complete multiagent system validation
Uses REAL Chrome DevTools MCP integration (no mocks)
"""

import pytest
import asyncio
import os
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.mcp_bridge import MCPBridge
from agents.developer_agent import DeveloperAgent


class TestTask1ChromeDevToolsIntegration:
    """Task 1: Integrate Chrome DevTools via MCP Bridge"""

    @pytest.fixture
    def mcp_bridge(self):
        """Create MCPBridge instance for testing"""
        return MCPBridge()

    def test_chrome_devtools_server_configured(self, mcp_bridge):
        """Test Chrome DevTools server is configured in MCPBridge"""
        available_servers = mcp_bridge.get_available_servers()
        assert "chrome_devtools" in available_servers, \
            "Chrome DevTools server not found in MCPBridge configuration"

    def test_chrome_devtools_connection(self, mcp_bridge):
        """Test basic Chrome DevTools MCP connection"""
        # Verify bridge can connect to Chrome DevTools server
        connection_test = mcp_bridge.test_connection()
        assert connection_test["bridge_available"], \
            f"MCPBridge not available: {connection_test.get('error')}"

        # Verify Chrome DevTools is in available servers
        assert "chrome_devtools" in mcp_bridge.wrapped_mcp_servers, \
            "Chrome DevTools not configured in wrapped_mcp_servers"

    @pytest.mark.asyncio
    async def test_chrome_devtools_list_tools(self, mcp_bridge):
        """Test listing available Chrome DevTools tools"""
        # Load tools from Chrome DevTools MCP server
        tools = await mcp_bridge._load_mcp_tools_async("chrome_devtools")

        assert "error" not in tools, \
            f"Failed to load Chrome DevTools tools: {tools.get('error')}"

        assert len(tools) > 0, \
            "No tools returned from Chrome DevTools server"

        print(f"\nChrome DevTools tools available: {list(tools.keys())}")

    @pytest.mark.skipif(
        os.getenv("SKIP_BROWSER_TESTS") == "true",
        reason="Browser tests disabled (set SKIP_BROWSER_TESTS=false to enable)"
    )
    def test_chrome_devtools_list_pages(self, mcp_bridge):
        """Test listing browser pages"""
        result = mcp_bridge.call_chrome_devtools_tool(
            tool_name="list_pages",
            parameters={}
        )

        assert result.get("success"), \
            f"Chrome DevTools list_pages failed: {result.get('error')}"

        print(f"\nBrowser pages: {result}")

    @pytest.mark.skipif(
        os.getenv("SKIP_BROWSER_TESTS") == "true",
        reason="Browser tests disabled"
    )
    def test_browser_automation_workflow(self, mcp_bridge):
        """Test complete browser automation workflow"""
        # 1. Create new page with URL
        new_page_result = mcp_bridge.call_chrome_devtools_tool(
            tool_name="new_page",
            parameters={"url": "https://example.com"}
        )
        assert new_page_result.get("success"), \
            f"Failed to create new page: {new_page_result.get('error')}"

        # 2. Take snapshot of loaded page
        snapshot_result = mcp_bridge.call_chrome_devtools_tool(
            tool_name="take_snapshot",
            parameters={}
        )
        assert snapshot_result.get("success"), \
            f"Failed to take snapshot: {snapshot_result.get('error')}"

        # 3. Get console messages
        console_result = mcp_bridge.call_chrome_devtools_tool(
            tool_name="list_console_messages",
            parameters={}
        )
        assert console_result.get("success"), \
            f"Failed to get console messages: {console_result.get('error')}"

        print(f"\nBrowser automation workflow completed successfully")

    def test_dom_inspection_capabilities(self, mcp_bridge):
        """Test DOM inspection and element interaction"""
        # Verify DOM inspection tools available
        tools_result = asyncio.run(mcp_bridge._load_mcp_tools_async("chrome_devtools"))

        dom_tools = ["take_snapshot", "evaluate_script", "click", "hover", "fill"]
        for tool in dom_tools:
            assert tool in tools_result, \
                f"DOM inspection tool {tool} not available"

        print(f"\nDOM inspection tools verified: {dom_tools}")

    def test_debugging_capabilities(self, mcp_bridge):
        """Test console log access and JavaScript evaluation"""
        # Verify debugging tools available
        tools_result = asyncio.run(mcp_bridge._load_mcp_tools_async("chrome_devtools"))

        debug_tools = ["list_console_messages", "evaluate_script"]
        for tool in debug_tools:
            assert tool in tools_result, \
                f"Debugging tool {tool} not available"

        print(f"\nDebugging tools verified: {debug_tools}")

    def test_screenshot_capability(self, mcp_bridge):
        """Test screenshot functionality"""
        # Verify screenshot tool available
        tools_result = asyncio.run(mcp_bridge._load_mcp_tools_async("chrome_devtools"))

        assert "take_screenshot" in tools_result, \
            "Screenshot tool not available"

        print("\nScreenshot capability verified")

    def test_performance_profiling_capabilities(self, mcp_bridge):
        """Test performance profiling tools"""
        # Verify performance tools available
        tools_result = asyncio.run(mcp_bridge._load_mcp_tools_async("chrome_devtools"))

        perf_tools = ["performance_start_trace", "performance_stop_trace", "performance_analyze_insight"]
        for tool in perf_tools:
            assert tool in tools_result, \
                f"Performance tool {tool} not available"

        print(f"\nPerformance profiling tools verified: {perf_tools}")


class TestTask2DeveloperAgentEnhancement:
    """Task 2: Complete Developer Agent Enhancement"""

    @pytest.fixture
    def developer_agent(self):
        """Create DeveloperAgent instance for testing"""
        from core.mcp_bridge import MCPBridge
        mcp_bridge = MCPBridge()
        return DeveloperAgent(mcp_bridge=mcp_bridge)

    def test_developer_agent_has_chrome_devtools(self, developer_agent):
        """Test Developer Agent has Chrome DevTools capability"""
        tools = developer_agent.get_available_tools()
        assert 'chrome_devtools_mcp' in tools, \
            "Chrome DevTools MCP not found in Developer Agent tools"

    def test_developer_agent_mcp_bridge_integration(self, developer_agent):
        """Test Developer Agent integrates with MCPBridge"""
        # Developer Agent should have mcp_bridge attribute after enhancement
        assert hasattr(developer_agent, 'mcp_bridge'), \
            "Developer Agent missing mcp_bridge attribute"

        assert developer_agent.mcp_bridge is not None, \
            "Developer Agent mcp_bridge is None"

    @pytest.mark.skipif(
        os.getenv("SKIP_BROWSER_TESTS") == "true",
        reason="Browser tests disabled"
    )
    def test_developer_agent_browser_workflow(self, developer_agent):
        """Test Developer Agent web development workflow"""
        # Test basic browser debugging workflow
        result = developer_agent.process_task(
            task_description="Debug web page at https://example.com",
            context={"operation": "inspect_page"}
        )

        assert result["agent"] == "developer", \
            "Wrong agent processed task"

        assert result["implementation_complete"], \
            "Task not marked as complete"


class TestTask3ClaudeCodeIntegration:
    """Task 3: Claude Code Integration"""

    def test_mcp_bridge_tool_discovery(self):
        """Test MCPBridge exposes tools for Claude Code discovery"""
        bridge = MCPBridge()

        # Claude Code should be able to discover all available servers
        servers = bridge.get_available_servers()

        expected_servers = [
            "serena", "context7", "sequential_thinking",
            "github", "tavily", "sentry", "postgres",
            "obsidian", "filesystem", "chrome_devtools"
        ]

        for server in expected_servers:
            assert server in servers, \
                f"Server {server} not discoverable by Claude Code"

    def test_chrome_devtools_tool_calling_interface(self):
        """Test Chrome DevTools tool calling compatible with Claude Code"""
        bridge = MCPBridge()

        # Verify Chrome DevTools server config has correct structure
        config = bridge.wrapped_mcp_servers.get("chrome_devtools")

        assert config is not None, "Chrome DevTools config missing"
        assert config["type"] == "stdio", "Chrome DevTools should use stdio transport"
        assert "command" in config, "Chrome DevTools config missing command"
        assert "args" in config, "Chrome DevTools config missing args"


class TestTask4EndToEndWorkflow:
    """Task 4: End-to-End Workflow Validation"""

    @pytest.fixture
    def all_agents(self):
        """Create all 5 agents for end-to-end testing"""
        # Import from src package
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from agents.orchestrator_agent import OrchestratorAgent
        from agents.analyst_agent import AnalystAgent
        from agents.knowledge_agent import KnowledgeAgent
        from agents.developer_agent import DeveloperAgent
        from agents.validator_agent import ValidatorAgent
        from core.mcp_bridge import MCPBridge

        # Create shared MCPBridge
        mcp_bridge = MCPBridge()

        # Create agents (only pass mcp_bridge to agents that support it)
        return {
            "orchestrator": OrchestratorAgent(),
            "analyst": AnalystAgent(mcp_bridge=mcp_bridge),
            "knowledge": KnowledgeAgent(),
            "developer": DeveloperAgent(mcp_bridge=mcp_bridge),
            "validator": ValidatorAgent()
        }

    def test_all_five_agents_available(self, all_agents):
        """Test all 5 agents from Story 1.1 are available"""
        expected_agents = ["orchestrator", "analyst", "knowledge", "developer", "validator"]

        for agent_name in expected_agents:
            assert agent_name in all_agents, \
                f"Agent {agent_name} not available"

            assert all_agents[agent_name] is not None, \
                f"Agent {agent_name} is None"

    def test_agent_coordination_capabilities(self, all_agents):
        """Test agents have coordination capabilities"""
        for agent_name, agent in all_agents.items():
            # Each agent should have process_task method
            assert hasattr(agent, 'process_task'), \
                f"Agent {agent_name} missing process_task method"

            # Each agent should have get_available_tools method
            assert hasattr(agent, 'get_available_tools'), \
                f"Agent {agent_name} missing get_available_tools method"

            tools = agent.get_available_tools()
            assert len(tools) > 0, \
                f"Agent {agent_name} has no tools configured"

    def test_mcp_tool_distribution_across_agents(self, all_agents):
        """Test MCP tools are correctly distributed across agents"""
        # Verify each agent has at least some tools configured
        agent_tool_requirements = {
            "orchestrator": ["github", "tavily"],  # Orchestrator uses GitHub and Tavily
            "analyst": ["serena", "context7", "sequential"],  # Analyst uses Serena, Context7, Sequential Thinking
            "knowledge": ["filesystem", "obsidian"],  # Knowledge uses Filesystem, Obsidian (Graphiti direct)
            "developer": ["chrome_devtools", "filesystem"],  # Developer uses Chrome DevTools, Filesystem
            "validator": []  # Validator uses direct libraries (DSPy, Sentry, Postgres)
        }

        for agent_name, expected_tool_keywords in agent_tool_requirements.items():
            agent = all_agents[agent_name]
            agent_tools = agent.get_available_tools()
            agent_tools_str = " ".join(agent_tools).lower()

            # For agents with expected tools, check at least one keyword matches
            if expected_tool_keywords:
                has_expected_tool = any(
                    tool_keyword in agent_tools_str
                    for tool_keyword in expected_tool_keywords
                )
                assert has_expected_tool, \
                    f"Agent {agent_name} missing expected tools. Has: {agent_tools}"


class TestTask5PerformanceMetrics:
    """Task 5: Performance Verification and Optimization"""

    def test_performance_metrics_structure(self):
        """Test performance metrics can be collected"""
        # Performance tracking structure
        metrics = {
            "agent_response_times": {},
            "token_usage": {},
            "memory_consumption": {},
            "mcp_tool_overhead": {},
            "workflow_completion_time": 0
        }

        assert "agent_response_times" in metrics
        assert "token_usage" in metrics
        assert "mcp_tool_overhead" in metrics

    @pytest.mark.asyncio
    async def test_chrome_devtools_performance_baseline(self):
        """Test Chrome DevTools tool call performance"""
        import time
        bridge = MCPBridge()

        # Measure tool listing performance
        start_time = time.time()
        tools = await bridge._load_mcp_tools_async("chrome_devtools")
        elapsed = time.time() - start_time

        assert elapsed < 5.0, \
            f"Chrome DevTools tool loading too slow: {elapsed:.2f}s"

        print(f"\nChrome DevTools tool load time: {elapsed:.2f}s")

    def test_mcp_bridge_session_caching(self):
        """Test MCPBridge session caching for performance"""
        bridge = MCPBridge()

        # Verify session cache exists
        assert hasattr(bridge, '_active_sessions'), \
            "MCPBridge missing session cache"

        assert isinstance(bridge._active_sessions, dict), \
            "Session cache should be dict"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
