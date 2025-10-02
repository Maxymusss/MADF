"""
Story 1.2: Real Analyst Agent Integration Tests
NO MOCKS - Uses real MCP bridge and actual codebase files

Test Coverage:
- Task 1: Real Serena MCP integration with actual codebase files
- Task 2: Context7 MCP-use integration (using bridge methods, not mocked)
- Task 3: Sequential Thinking MCP-use integration (using bridge methods, not mocked)
- Task 4: Complete Analyst Agent implementation with real tool calls
- Task 5: End-to-end integration testing with real operations
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mcp_bridge import MCPBridge
from src.agents.analyst_agent import AnalystAgent


class TestTask1SerenaMCPRealIntegration:
    """Task 1: Real Serena MCP Integration for Semantic Code Search"""

    def test_serena_mcp_server_configuration(self):
        """Subtask 1.1: Configure Serena MCP server connection"""
        bridge = MCPBridge()

        # Verify Serena is registered as direct MCP server (stdio transport)
        assert "serena" in bridge.direct_mcp_servers
        assert bridge.direct_mcp_servers["serena"]["type"] == "stdio"
        assert bridge.direct_mcp_servers["serena"]["command"] == "npx"

    def test_serena_tool_loading(self):
        """Subtask 1.2: Implement serena tool loading via direct MCP protocol"""
        bridge = MCPBridge()
        serena_tools = bridge.load_mcp_tools("serena")

        # Verify LSP-based semantic search tools are loaded
        assert "find_symbol" in serena_tools
        assert "find_referencing_symbols" in serena_tools
        assert "search_for_pattern" in serena_tools
        assert "get_symbols_overview" in serena_tools

        # Verify tool descriptions
        assert "LSP" in serena_tools["find_symbol"] or "semantic" in serena_tools["find_symbol"]

    def test_find_symbol_on_real_file(self):
        """Subtask 1.3: Test find_symbol on real codebase file"""
        bridge = MCPBridge()

        # Test with actual AnalystAgent class in codebase
        result = bridge.call_serena_tool(
            "find_symbol",
            {
                "name_path": "AnalystAgent",
                "relative_path": "src/agents/analyst_agent.py",
                "include_body": True
            }
        )

        # Verify real symbol was found
        assert result["success"] is True
        assert "symbol_info" in result
        assert result["symbol_info"]["name"] == "AnalystAgent"
        assert "analyst_agent.py" in result["symbol_info"]["file"]

    def test_find_referencing_symbols_on_real_file(self):
        """Subtask 1.3: Test find_referencing_symbols on real codebase"""
        bridge = MCPBridge()

        # Find real references to BaseAgent class
        result = bridge.call_serena_tool(
            "find_referencing_symbols",
            {
                "name_path": "BaseAgent",
                "relative_path": "src/agents/base_agent.py"
            }
        )

        # Verify real references were found
        assert result["success"] is True
        assert "references" in result
        assert isinstance(result["references"], list)

    def test_search_for_pattern_on_real_codebase(self):
        """Subtask 1.3: Test search_for_pattern on real codebase"""
        bridge = MCPBridge()

        # Search for real agent class pattern
        result = bridge.call_serena_tool(
            "search_for_pattern",
            {
                "substring_pattern": "class.*Agent",
                "relative_path": "src/agents"
            }
        )

        # Verify real matches were found
        assert result["success"] is True
        assert "matches" in result
        assert isinstance(result["matches"], list)
        # Should find at least AnalystAgent
        assert len(result["matches"]) >= 1

    def test_get_symbols_overview_on_real_file(self):
        """Subtask 1.3: Test get_symbols_overview on real file"""
        bridge = MCPBridge()

        # Get symbols from real analyst_agent.py file
        result = bridge.call_serena_tool(
            "get_symbols_overview",
            {"relative_path": "src/agents/analyst_agent.py"}
        )

        # Verify real symbols were extracted
        assert result["success"] is True
        assert "symbols" in result
        assert isinstance(result["symbols"], list)

        # Should find AnalystAgent class
        symbol_names = [s["name"] for s in result["symbols"]]
        assert "AnalystAgent" in symbol_names

    def test_python_language_support_real_file(self):
        """Subtask 1.4: Validate Python language support with real file"""
        bridge = MCPBridge()

        # Test Python file (real)
        py_result = bridge.call_serena_tool(
            "find_symbol",
            {
                "name_path": "AnalystAgent",
                "relative_path": "src/agents/analyst_agent.py"
            }
        )
        assert py_result["success"] is True
        assert "symbol_info" in py_result

    def test_serena_error_handling_nonexistent_file(self):
        """Subtask 1.4: Test error handling for nonexistent file"""
        bridge = MCPBridge()

        # Test with invalid path
        result = bridge.call_serena_tool(
            "find_symbol",
            {
                "name_path": "FakeClass",
                "relative_path": "nonexistent/file.py"
            }
        )

        # Should gracefully handle error
        assert result["success"] is False
        assert "error" in result


class TestTask2Context7RealIntegration:
    """Task 2: Real Context7 via MCP-use Integration"""

    def test_context7_mcp_use_configuration(self):
        """Subtask 2.1: Configure Context7 MCP server in MCP-use wrapper"""
        bridge = MCPBridge()

        # Verify Context7 is registered in wrapped servers
        assert "context7" in bridge.wrapped_mcp_servers
        assert bridge.wrapped_mcp_servers["context7"]["type"] == "wrapped"
        assert bridge.wrapped_mcp_servers["context7"]["package"] == "@upstash/context7-mcp"

    def test_context7_tool_loading(self):
        """Subtask 2.2: Implement context7 tool loading"""
        bridge = MCPBridge()
        context7_tools = bridge.load_mcp_tools("context7")

        # Verify tools are loaded
        assert "search_docs" in context7_tools
        assert "get_package_docs" in context7_tools

        # Verify tool descriptions exist
        assert isinstance(context7_tools["get_package_docs"], str)
        assert len(context7_tools["get_package_docs"]) > 0

    def test_documentation_retrieval_method(self):
        """Subtask 2.3: Test documentation retrieval methods"""
        bridge = MCPBridge()

        # Call real bridge method (not mocked)
        result = bridge.call_context7_tool(
            "get_package_docs",
            {
                "package_name": "langgraph",
                "version": "0.2.0"
            }
        )

        # Verify real call executed
        assert result["success"] is True
        assert "documentation" in result
        assert result["documentation"]["package"] == "langgraph"
        assert result["documentation"]["version"] == "0.2.0"

    def test_rate_limiting_and_caching(self):
        """Subtask 2.4: Test real caching implementation"""
        bridge = MCPBridge()

        # First call should NOT be cached
        result1 = bridge.call_context7_tool(
            "get_package_docs",
            {"package_name": "pytest", "version": "7.0.0"}
        )

        assert result1["success"] is True
        assert result1.get("cached", False) is False

        # Second identical call should be cached
        result2 = bridge.call_context7_tool(
            "get_package_docs",
            {"package_name": "pytest", "version": "7.0.0"}
        )

        assert result2["success"] is True
        assert result2["cached"] is True

        # Verify cache is working
        assert bridge._context7_cache is not None
        assert len(bridge._context7_cache) > 0


class TestTask3SequentialThinkingRealIntegration:
    """Task 3: Real Sequential Thinking via MCP-use Integration"""

    def test_sequential_thinking_mcp_use_configuration(self):
        """Subtask 3.1: Configure Sequential Thinking MCP server"""
        bridge = MCPBridge()

        # Verify Sequential Thinking is registered
        assert "sequential_thinking" in bridge.wrapped_mcp_servers
        assert bridge.wrapped_mcp_servers["sequential_thinking"]["type"] == "wrapped"
        assert bridge.wrapped_mcp_servers["sequential_thinking"]["package"] == "@modelcontextprotocol/server-sequential-thinking"

    def test_sequential_thinking_tool_loading(self):
        """Subtask 3.2: Implement sequential reasoning tool access"""
        bridge = MCPBridge()
        seq_tools = bridge.load_mcp_tools("sequential_thinking")

        # Verify tools loaded
        assert "reason" in seq_tools
        assert "analyze_complex_problem" in seq_tools

    def test_complex_analysis_workflow_support(self):
        """Subtask 3.3: Test complex analysis workflow"""
        bridge = MCPBridge()

        # Call real bridge method
        result = bridge.call_sequential_thinking_tool(
            "analyze_complex_problem",
            {
                "problem": "Analyze MADF codebase architecture patterns",
                "context": {"codebase": "MADF"}
            }
        )

        # Verify real execution
        assert result["success"] is True
        assert "reasoning_steps" in result
        assert isinstance(result["reasoning_steps"], list)
        assert len(result["reasoning_steps"]) > 0

    def test_reasoning_chain_execution(self):
        """Subtask 3.4: Test reasoning chain execution"""
        bridge = MCPBridge()

        # Execute real reasoning chain
        result = bridge.call_sequential_thinking_tool(
            "reason",
            {"query": "What are the dependencies between agents in MADF?"}
        )

        # Verify reasoning chain generated
        assert result["success"] is True
        assert "reasoning_chain" in result
        assert isinstance(result["reasoning_chain"], list)
        assert len(result["reasoning_chain"]) > 0


class TestTask4AnalystAgentRealImplementation:
    """Task 4: Complete Analyst Agent with Real Tool Integration"""

    def test_analyst_agent_tool_integration(self):
        """Subtask 4.1: Verify all three tools integrated"""
        agent = AnalystAgent()
        tools = agent.get_available_tools()

        # Verify all tools present
        assert "serena_mcp" in tools
        assert "context7_mcp" in tools
        assert "sequential_thinking_mcp" in tools

    def test_code_analysis_workflow_with_real_serena(self):
        """Subtask 4.2: Test code analysis with real Serena calls"""
        agent = AnalystAgent()

        # Analyze real file
        result = agent.analyze_code_structure(
            target="src/agents/analyst_agent.py",
            analysis_type="semantic_search"
        )

        # Verify real analysis completed
        assert result["success"] is True
        assert result["tool_used"] == "serena_mcp"
        assert result["analysis_complete"] is True
        assert "symbols_found" in result
        assert isinstance(result["symbols_found"], list)

    def test_code_analysis_workflow_with_real_context7(self):
        """Subtask 4.2: Test documentation retrieval with real Context7"""
        agent = AnalystAgent()

        # Get real documentation
        result = agent.get_documentation(
            package="pydantic",
            version="2.0"
        )

        # Verify real retrieval
        assert result["tool_used"] == "context7_mcp"
        assert result["documentation_retrieved"] is True
        assert result["package"] == "pydantic"

    def test_code_analysis_workflow_with_real_sequential_thinking(self):
        """Subtask 4.2: Test reasoning with real Sequential Thinking"""
        agent = AnalystAgent()

        # Execute real reasoning
        result = agent.reason_about_architecture(
            question="How do agents communicate in MADF?"
        )

        # Verify real reasoning executed
        assert result["tool_used"] == "sequential_thinking_mcp"
        assert "reasoning_steps" in result
        assert result["success"] is True

    def test_token_efficiency_tracking(self):
        """Subtask 4.3: Test real token efficiency tracking"""
        agent = AnalystAgent()

        # Track tokens during real analysis
        result = agent.analyze_code_structure(
            target="src/agents/analyst_agent.py",
            analysis_type="semantic_search",
            track_tokens=True
        )

        # Verify token metrics calculated
        assert "token_metrics" in result
        assert result["token_metrics"]["tokens_used"] > 0
        assert result["token_metrics"]["efficiency_ratio"] > 0
        assert result["token_metrics"]["total_tokens"] > 0

    def test_langgraph_state_graph_integration(self):
        """Subtask 4.4: Test LangGraph StateGraph compatibility"""
        agent = AnalystAgent()

        # Verify StateGraph interface
        assert hasattr(agent, "process_task")
        assert callable(agent.process_task)

        # Execute real task processing
        result = agent.process_task(
            task_description="Analyze codebase structure",
            context={"target": "src/agents"}
        )

        # Verify processing completed
        assert "analysis_complete" in result
        assert result["analysis_complete"] is True


class TestTask5EndToEndRealIntegration:
    """Task 5: End-to-End Real Integration Testing"""

    def test_full_analyst_workflow_real(self):
        """Subtask 5.1: Test full analyst workflow with real tools"""
        agent = AnalystAgent()

        # Step 1: Real semantic search with Serena
        search_result = agent.analyze_code_structure(
            target="src/agents/analyst_agent.py",
            analysis_type="semantic_search"
        )
        assert search_result["success"] is True
        assert search_result["analysis_complete"] is True

        # Step 2: Real documentation with Context7
        doc_result = agent.get_documentation(
            package="langgraph",
            version="0.2.0"
        )
        assert doc_result["documentation_retrieved"] is True

        # Step 3: Real reasoning with Sequential Thinking
        reasoning_result = agent.reason_about_architecture(
            question="What patterns are used in the agent architecture?"
        )
        assert "reasoning_steps" in reasoning_result
        assert reasoning_result["success"] is True

    def test_python_language_support_validation(self):
        """Subtask 5.2: Validate Python language support via Serena"""
        bridge = MCPBridge()

        # Test multiple Python files in codebase
        python_files = [
            "src/agents/analyst_agent.py",
            "src/agents/base_agent.py",
            "src/core/mcp_bridge.py"
        ]

        for py_file in python_files:
            result = bridge.call_serena_tool(
                "get_symbols_overview",
                {"relative_path": py_file}
            )
            # Should successfully process Python files
            assert result["success"] is True
            assert "symbols" in result

    def test_token_efficiency_vs_traditional_reading(self):
        """Subtask 5.3: Measure real token efficiency"""
        agent = AnalystAgent()

        # Perform semantic search with token tracking
        semantic_result = agent.analyze_code_structure(
            target="src/agents/analyst_agent.py",
            analysis_type="semantic_search",
            track_tokens=True
        )

        # Verify efficiency metrics calculated
        semantic_tokens = semantic_result["token_metrics"]["tokens_used"]
        efficiency_ratio = semantic_result["token_metrics"]["efficiency_ratio"]

        # Semantic search should use tokens efficiently
        assert semantic_tokens > 0
        assert efficiency_ratio > 0

        # Should be more efficient than reading full file
        # (Full file ~2000 tokens, semantic ~300 tokens per symbol)
        symbols_count = len(semantic_result["symbols_found"])
        assert semantic_tokens < 2000  # More efficient than full file read

    def test_error_handling_and_fallback(self):
        """Subtask 5.4: Test real error handling"""
        agent = AnalystAgent()

        # Test with invalid target
        result = agent.analyze_code_structure(
            target="nonexistent/fake_file.py",
            analysis_type="semantic_search"
        )

        # Verify error handled gracefully
        assert result["success"] is False
        assert "error" in result
        assert "fallback_attempted" in result
        assert result["fallback_attempted"] is True

    def test_tool_usage_patterns_documentation(self):
        """Subtask 5.5: Verify tool usage patterns"""
        agent = AnalystAgent()

        # Get real usage patterns
        usage_patterns = agent.get_tool_usage_patterns()

        # Verify all tools documented
        assert "serena_mcp" in usage_patterns
        assert "context7_mcp" in usage_patterns
        assert "sequential_thinking_mcp" in usage_patterns

        # Verify pattern structure
        for tool, pattern in usage_patterns.items():
            assert "description" in pattern
            assert "example_usage" in pattern
            assert "when_to_use" in pattern

            # Verify non-empty documentation
            assert len(pattern["description"]) > 0
            assert len(pattern["example_usage"]) > 0
            assert len(pattern["when_to_use"]) > 0