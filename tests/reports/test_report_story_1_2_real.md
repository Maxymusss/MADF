============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-8.4.2, pluggy-1.6.0 -- D:\dev\MADF\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\dev\MADF
configfile: pytest.ini
plugins: anyio-4.10.0, langsmith-0.4.27, asyncio-1.2.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 27 items

tests/test_story_1_2_real_analyst_agent.py::TestTask1SerenaMCPRealIntegration::test_serena_mcp_server_configuration PASSED [  3%]
tests/test_story_1_2_real_analyst_agent.py::TestTask1SerenaMCPRealIntegration::test_serena_tool_loading PASSED [  7%]
tests/test_story_1_2_real_analyst_agent.py::TestTask1SerenaMCPRealIntegration::test_find_symbol_on_real_file PASSED [ 11%]
tests/test_story_1_2_real_analyst_agent.py::TestTask1SerenaMCPRealIntegration::test_find_referencing_symbols_on_real_file PASSED [ 14%]
tests/test_story_1_2_real_analyst_agent.py::TestTask1SerenaMCPRealIntegration::test_search_for_pattern_on_real_codebase PASSED [ 18%]
tests/test_story_1_2_real_analyst_agent.py::TestTask1SerenaMCPRealIntegration::test_get_symbols_overview_on_real_file PASSED [ 22%]
tests/test_story_1_2_real_analyst_agent.py::TestTask1SerenaMCPRealIntegration::test_python_language_support_real_file PASSED [ 25%]
tests/test_story_1_2_real_analyst_agent.py::TestTask1SerenaMCPRealIntegration::test_serena_error_handling_nonexistent_file PASSED [ 29%]
tests/test_story_1_2_real_analyst_agent.py::TestTask2Context7RealIntegration::test_context7_mcp_use_configuration PASSED [ 33%]
tests/test_story_1_2_real_analyst_agent.py::TestTask2Context7RealIntegration::test_context7_tool_loading PASSED [ 37%]
tests/test_story_1_2_real_analyst_agent.py::TestTask2Context7RealIntegration::test_documentation_retrieval_method PASSED [ 40%]
tests/test_story_1_2_real_analyst_agent.py::TestTask2Context7RealIntegration::test_rate_limiting_and_caching PASSED [ 44%]
tests/test_story_1_2_real_analyst_agent.py::TestTask3SequentialThinkingRealIntegration::test_sequential_thinking_mcp_use_configuration PASSED [ 48%]
tests/test_story_1_2_real_analyst_agent.py::TestTask3SequentialThinkingRealIntegration::test_sequential_thinking_tool_loading PASSED [ 51%]
tests/test_story_1_2_real_analyst_agent.py::TestTask3SequentialThinkingRealIntegration::test_complex_analysis_workflow_support PASSED [ 55%]
tests/test_story_1_2_real_analyst_agent.py::TestTask3SequentialThinkingRealIntegration::test_reasoning_chain_execution PASSED [ 59%]
tests/test_story_1_2_real_analyst_agent.py::TestTask4AnalystAgentRealImplementation::test_analyst_agent_tool_integration PASSED [ 62%]
tests/test_story_1_2_real_analyst_agent.py::TestTask4AnalystAgentRealImplementation::test_code_analysis_workflow_with_real_serena PASSED [ 66%]
tests/test_story_1_2_real_analyst_agent.py::TestTask4AnalystAgentRealImplementation::test_code_analysis_workflow_with_real_context7 PASSED [ 70%]
tests/test_story_1_2_real_analyst_agent.py::TestTask4AnalystAgentRealImplementation::test_code_analysis_workflow_with_real_sequential_thinking PASSED [ 74%]
tests/test_story_1_2_real_analyst_agent.py::TestTask4AnalystAgentRealImplementation::test_token_efficiency_tracking PASSED [ 77%]
tests/test_story_1_2_real_analyst_agent.py::TestTask4AnalystAgentRealImplementation::test_langgraph_state_graph_integration PASSED [ 81%]
tests/test_story_1_2_real_analyst_agent.py::TestTask5EndToEndRealIntegration::test_full_analyst_workflow_real PASSED [ 85%]
tests/test_story_1_2_real_analyst_agent.py::TestTask5EndToEndRealIntegration::test_python_language_support_validation PASSED [ 88%]
tests/test_story_1_2_real_analyst_agent.py::TestTask5EndToEndRealIntegration::test_token_efficiency_vs_traditional_reading PASSED [ 92%]
tests/test_story_1_2_real_analyst_agent.py::TestTask5EndToEndRealIntegration::test_error_handling_and_fallback PASSED [ 96%]
tests/test_story_1_2_real_analyst_agent.py::TestTask5EndToEndRealIntegration::test_tool_usage_patterns_documentation PASSED [100%]

============================= 27 passed in 0.03s ==============================
