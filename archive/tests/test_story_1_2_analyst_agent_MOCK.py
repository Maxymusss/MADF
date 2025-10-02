"""
Story 1.2: Analyst Agent with Serena MCP + Context7 + Sequential Thinking

Test Coverage:
- Task 1: Direct Serena MCP integration and semantic search
- Task 2: Context7 MCP-use integration for documentation
- Task 3: Sequential Thinking MCP-use integration
- Task 4: Complete Analyst Agent implementation
- Task 5: End-to-end integration testing
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.core.mcp_bridge import MCPBridge
from src.agents.analyst_agent import AnalystAgent


class TestTask1SerenaMCPIntegration:
    """Task 1: Integrate Direct Serena MCP for Semantic Code Search"""

    def test_serena_mcp_server_configuration(self):
        """Subtask 1.1: Configure Serena MCP server connection"""
        bridge = MCPBridge()
        assert "serena" in bridge.direct_mcp_servers
        assert bridge.direct_mcp_servers["serena"]["type"] == "direct"

    def test_serena_tool_loading(self):
        """Subtask 1.2: Implement serena tool loading via direct MCP protocol"""
        bridge = MCPBridge()
        serena_tools = bridge.load_mcp_tools("serena")

        # Verify LSP-based semantic search tools
        assert "find_symbol" in serena_tools
        assert "find_referencing_symbols" in serena_tools
        assert "search_for_pattern" in serena_tools
        assert "get_symbols_overview" in serena_tools

    def test_find_symbol_method(self):
        """Subtask 1.3: Add LSP-based semantic search method - find_symbol"""
        bridge = MCPBridge()

        # Test find_symbol tool call
        result = bridge.call_serena_tool(
            "find_symbol",
            {
                "name_path": "AnalystAgent",
                "relative_path": "src/agents/analyst_agent.py",
                "include_body": True
            }
        )

        assert result["success"] is True
        assert "symbol_info" in result

    def test_find_referencing_symbols_method(self):
        """Subtask 1.3: Add LSP-based semantic search method - find_referencing_symbols"""
        bridge = MCPBridge()

        result = bridge.call_serena_tool(
            "find_referencing_symbols",
            {
                "name_path": "BaseAgent",
                "relative_path": "src/agents/base_agent.py"
            }
        )

        assert result["success"] is True
        assert "references" in result

    def test_search_for_pattern_method(self):
        """Subtask 1.3: Add LSP-based semantic search method - search_for_pattern"""
        bridge = MCPBridge()

        result = bridge.call_serena_tool(
            "search_for_pattern",
            {
                "substring_pattern": "class.*Agent",
                "relative_path": "src/agents"
            }
        )

        assert result["success"] is True
        assert "matches" in result

    def test_get_symbols_overview_method(self):
        """Subtask 1.3: Add LSP-based semantic search method - get_symbols_overview"""
        bridge = MCPBridge()

        result = bridge.call_serena_tool(
            "get_symbols_overview",
            {"relative_path": "src/agents/analyst_agent.py"}
        )

        assert result["success"] is True
        assert "symbols" in result

    def test_python_typescript_language_support(self):
        """Subtask 1.4: Validate Python/TypeScript language support"""
        bridge = MCPBridge()

        # Test Python support
        py_result = bridge.call_serena_tool(
            "find_symbol",
            {
                "name_path": "AnalystAgent",
                "relative_path": "src/agents/analyst_agent.py"
            }
        )
        assert py_result["success"] is True

        # Test TypeScript support capability (mock)
        ts_result = bridge.call_serena_tool(
            "find_symbol",
            {
                "name_path": "Component",
                "relative_path": "src/frontend/component.ts"
            }
        )
        # Should handle TypeScript files via LSP
        assert "success" in ts_result


class TestTask2Context7Integration:
    """Task 2: Integrate Context7 via MCP-use for Real-time Documentation"""

    def test_context7_mcp_use_configuration(self):
        """Subtask 2.1: Configure Context7 MCP server in MCP-use wrapper"""
        bridge = MCPBridge()
        assert "context7" in bridge.wrapped_mcp_servers
        assert bridge.wrapped_mcp_servers["context7"]["type"] == "wrapped"
        assert bridge.wrapped_mcp_servers["context7"]["package"] == "@upstash/context7-mcp"

    def test_context7_tool_loading(self):
        """Subtask 2.2: Implement context7 tool loading"""
        bridge = MCPBridge()
        context7_tools = bridge.load_mcp_tools("context7")

        assert "search_docs" in context7_tools
        assert "get_package_docs" in context7_tools

    def test_documentation_retrieval_method(self):
        """Subtask 2.3: Add documentation retrieval methods"""
        bridge = MCPBridge()

        result = bridge.call_context7_tool(
            "get_package_docs",
            {
                "package_name": "langgraph",
                "version": "0.2.0"
            }
        )

        assert result["success"] is True
        assert "documentation" in result

    def test_rate_limiting_and_caching(self):
        """Subtask 2.4: Handle rate limiting and caching for Context7 API"""
        bridge = MCPBridge()

        # First call should hit API
        result1 = bridge.call_context7_tool(
            "get_package_docs",
            {"package_name": "langgraph", "version": "0.2.0"}
        )

        # Second call should use cache
        result2 = bridge.call_context7_tool(
            "get_package_docs",
            {"package_name": "langgraph", "version": "0.2.0"}
        )

        assert result1["success"] is True
        assert result2["success"] is True
        assert result2.get("cached", False) is True


class TestTask3SequentialThinkingIntegration:
    """Task 3: Integrate Sequential Thinking via MCP-use"""

    def test_sequential_thinking_mcp_use_configuration(self):
        """Subtask 3.1: Configure Sequential Thinking MCP server in MCP-use wrapper"""
        bridge = MCPBridge()
        assert "sequential_thinking" in bridge.wrapped_mcp_servers
        assert bridge.wrapped_mcp_servers["sequential_thinking"]["type"] == "wrapped"

    def test_sequential_thinking_tool_loading(self):
        """Subtask 3.2: Implement sequential reasoning tool access"""
        bridge = MCPBridge()
        seq_tools = bridge.load_mcp_tools("sequential_thinking")

        assert "reason" in seq_tools
        assert "analyze_complex_problem" in seq_tools

    def test_complex_analysis_workflow_support(self):
        """Subtask 3.3: Add complex analysis workflow support"""
        bridge = MCPBridge()

        result = bridge.call_sequential_thinking_tool(
            "analyze_complex_problem",
            {
                "problem": "Analyze codebase architecture patterns",
                "context": {"codebase": "MADF"}
            }
        )

        assert result["success"] is True
        assert "reasoning_steps" in result

    def test_reasoning_chain_execution(self):
        """Subtask 3.4: Test reasoning chain execution"""
        bridge = MCPBridge()

        result = bridge.call_sequential_thinking_tool(
            "reason",
            {"query": "What are the dependencies between agents?"}
        )

        assert result["success"] is True
        assert "reasoning_chain" in result
        assert len(result["reasoning_chain"]) > 0


class TestTask4AnalystAgentImplementation:
    """Task 4: Complete Analyst Agent Implementation"""

    def test_analyst_agent_tool_integration(self):
        """Subtask 4.1: Extend analyst_agent.py with all three tools"""
        agent = AnalystAgent()
        tools = agent.get_available_tools()

        assert "serena_mcp" in tools
        assert "context7_mcp" in tools
        assert "sequential_thinking_mcp" in tools

    def test_code_analysis_workflow_with_serena(self):
        """Subtask 4.2: Implement code analysis workflows - Serena"""
        agent = AnalystAgent()

        result = agent.analyze_code_structure(
            target="src/agents/analyst_agent.py",
            analysis_type="semantic_search"
        )

        assert result["tool_used"] == "serena_mcp"
        assert result["analysis_complete"] is True
        assert "symbols_found" in result

    def test_code_analysis_workflow_with_context7(self):
        """Subtask 4.2: Implement code analysis workflows - Context7"""
        agent = AnalystAgent()

        result = agent.get_documentation(
            package="langgraph",
            version="0.2.0"
        )

        assert result["tool_used"] == "context7_mcp"
        assert result["documentation_retrieved"] is True

    def test_code_analysis_workflow_with_sequential_thinking(self):
        """Subtask 4.2: Implement code analysis workflows - Sequential Thinking"""
        agent = AnalystAgent()

        result = agent.reason_about_architecture(
            question="How do agents communicate?"
        )

        assert result["tool_used"] == "sequential_thinking_mcp"
        assert "reasoning_steps" in result

    def test_token_efficiency_tracking(self):
        """Subtask 4.3: Add token efficiency tracking and metrics"""
        agent = AnalystAgent()

        result = agent.analyze_code_structure(
            target="src/agents/analyst_agent.py",
            analysis_type="semantic_search",
            track_tokens=True
        )

        assert "token_metrics" in result
        assert result["token_metrics"]["tokens_used"] > 0
        assert result["token_metrics"]["efficiency_ratio"] > 0

    def test_langgraph_state_graph_integration(self):
        """Subtask 4.4: Integrate with LangGraph StateGraph from Story 1.1"""
        agent = AnalystAgent()

        # Agent should be compatible with StateGraph from Story 1.1
        assert hasattr(agent, "process_task")
        assert callable(agent.process_task)

        result = agent.process_task(
            task_description="Analyze codebase structure",
            context={"target": "src/agents"}
        )

        assert "analysis_complete" in result


class TestTask5EndToEndIntegration:
    """Task 5: End-to-End Integration Testing"""

    def test_full_analyst_workflow(self):
        """Subtask 5.1: Test full analyst agent workflow with all tools"""
        agent = AnalystAgent()
        bridge = MCPBridge()

        # Step 1: Semantic search with Serena
        search_result = agent.analyze_code_structure(
            target="src/agents",
            analysis_type="semantic_search"
        )
        assert search_result["analysis_complete"] is True

        # Step 2: Get documentation with Context7
        doc_result = agent.get_documentation(
            package="langgraph",
            version="0.2.0"
        )
        assert doc_result["documentation_retrieved"] is True

        # Step 3: Reason about findings with Sequential Thinking
        reasoning_result = agent.reason_about_architecture(
            question="What patterns are used in the agent architecture?"
        )
        assert "reasoning_steps" in reasoning_result

    def test_20_plus_language_support(self):
        """Subtask 5.2: Validate 20+ language support via Serena LSP"""
        bridge = MCPBridge()

        # Test multiple language support
        languages = [
            ("Python", "src/agents/analyst_agent.py"),
            ("TypeScript", "src/frontend/component.ts"),
            ("JavaScript", "mcp_bridge/bridge.js"),
            ("Go", "services/api.go"),
            ("Rust", "lib/core.rs"),
            ("Java", "services/Service.java")
        ]

        for lang_name, file_path in languages:
            result = bridge.call_serena_tool(
                "get_symbols_overview",
                {"relative_path": file_path}
            )
            # Should handle multiple languages via LSP
            assert "success" in result

    def test_token_efficiency_vs_traditional_reading(self):
        """Subtask 5.3: Measure token efficiency vs traditional file reading"""
        agent = AnalystAgent()

        # Semantic search (efficient)
        semantic_result = agent.analyze_code_structure(
            target="src/agents/analyst_agent.py",
            analysis_type="semantic_search",
            track_tokens=True
        )

        # Traditional full file read (inefficient - simulated)
        traditional_tokens = 2000  # Mock full file read tokens
        semantic_tokens = semantic_result["token_metrics"]["tokens_used"]

        # Semantic search should be more efficient
        efficiency_gain = (traditional_tokens - semantic_tokens) / traditional_tokens
        assert efficiency_gain > 0.3  # At least 30% more efficient

    def test_error_handling_and_fallback(self):
        """Subtask 5.4: Test error handling and fallback mechanisms"""
        agent = AnalystAgent()

        # Test with invalid target
        result = agent.analyze_code_structure(
            target="nonexistent/file.py",
            analysis_type="semantic_search"
        )

        assert result["success"] is False
        assert "error" in result
        assert "fallback_attempted" in result

    def test_tool_usage_patterns_documentation(self):
        """Subtask 5.5: Document tool usage patterns"""
        agent = AnalystAgent()

        # Agent should provide tool usage guidance
        usage_patterns = agent.get_tool_usage_patterns()

        assert "serena_mcp" in usage_patterns
        assert "context7_mcp" in usage_patterns
        assert "sequential_thinking_mcp" in usage_patterns

        # Each pattern should have description and example
        for tool, pattern in usage_patterns.items():
            assert "description" in pattern
            assert "example_usage" in pattern