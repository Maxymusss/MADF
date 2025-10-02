============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-8.4.2, pluggy-1.6.0 -- D:\dev\MADF\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: d:\dev\MADF
configfile: pytest.ini
plugins: anyio-4.10.0, langsmith-0.4.27, asyncio-1.2.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 20 items / 2 deselected / 18 selected

tests/test_story_1_6_end_to_end.py::TestTask1ChromeDevToolsIntegration::test_chrome_devtools_server_configured PASSED [  5%]
tests/test_story_1_6_end_to_end.py::TestTask1ChromeDevToolsIntegration::test_chrome_devtools_connection PASSED [ 11%]
tests/test_story_1_6_end_to_end.py::TestTask1ChromeDevToolsIntegration::test_chrome_devtools_list_tools PASSED [ 16%]
tests/test_story_1_6_end_to_end.py::TestTask1ChromeDevToolsIntegration::test_dom_inspection_capabilities PASSED [ 22%]
tests/test_story_1_6_end_to_end.py::TestTask1ChromeDevToolsIntegration::test_debugging_capabilities PASSED [ 27%]
tests/test_story_1_6_end_to_end.py::TestTask1ChromeDevToolsIntegration::test_screenshot_capability PASSED [ 33%]
tests/test_story_1_6_end_to_end.py::TestTask1ChromeDevToolsIntegration::test_performance_profiling_capabilities PASSED [ 38%]
tests/test_story_1_6_end_to_end.py::TestTask2DeveloperAgentEnhancement::test_developer_agent_has_chrome_devtools PASSED [ 44%]
tests/test_story_1_6_end_to_end.py::TestTask2DeveloperAgentEnhancement::test_developer_agent_mcp_bridge_integration PASSED [ 50%]
tests/test_story_1_6_end_to_end.py::TestTask2DeveloperAgentEnhancement::test_developer_agent_browser_workflow PASSED [ 55%]
tests/test_story_1_6_end_to_end.py::TestTask3ClaudeCodeIntegration::test_mcp_bridge_tool_discovery PASSED [ 61%]
tests/test_story_1_6_end_to_end.py::TestTask3ClaudeCodeIntegration::test_chrome_devtools_tool_calling_interface PASSED [ 66%]
tests/test_story_1_6_end_to_end.py::TestTask4EndToEndWorkflow::test_all_five_agents_available PASSED [ 72%]
tests/test_story_1_6_end_to_end.py::TestTask4EndToEndWorkflow::test_agent_coordination_capabilities PASSED [ 77%]
tests/test_story_1_6_end_to_end.py::TestTask4EndToEndWorkflow::test_mcp_tool_distribution_across_agents PASSED [ 83%]
tests/test_story_1_6_end_to_end.py::TestTask5PerformanceMetrics::test_performance_metrics_structure PASSED [ 88%]
tests/test_story_1_6_end_to_end.py::TestTask5PerformanceMetrics::test_chrome_devtools_performance_baseline PASSED [ 94%]
tests/test_story_1_6_end_to_end.py::TestTask5PerformanceMetrics::test_mcp_bridge_session_caching PASSED [100%]

====================== 18 passed, 2 deselected in 11.48s ======================
