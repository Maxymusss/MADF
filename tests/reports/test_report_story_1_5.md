============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-8.4.2, pluggy-1.6.0 -- D:\dev\MADF\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: d:\dev\MADF
configfile: pytest.ini
plugins: anyio-4.10.0, langsmith-0.4.27, asyncio-1.2.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 23 items

tests/test_story_1_5_real_orchestrator.py::TestTask1GitHubIntegration::test_github_client_initialization PASSED [  4%]
tests/test_story_1_5_real_orchestrator.py::TestTask1GitHubIntegration::test_search_repos PASSED [  8%]
tests/test_story_1_5_real_orchestrator.py::TestTask1GitHubIntegration::test_get_repo PASSED [ 13%]
tests/test_story_1_5_real_orchestrator.py::TestTask1GitHubIntegration::test_list_prs PASSED [ 17%]
tests/test_story_1_5_real_orchestrator.py::TestTask1GitHubIntegration::test_list_issues PASSED [ 21%]
tests/test_story_1_5_real_orchestrator.py::TestTask1GitHubIntegration::test_check_rate_limit PASSED [ 26%]
tests/test_story_1_5_real_orchestrator.py::TestTask1GitHubIntegration::test_read_only_mode_blocks_writes PASSED [ 30%]
tests/test_story_1_5_real_orchestrator.py::TestTask2TavilyIntegration::test_tavily_client_initialization PASSED [ 34%]
tests/test_story_1_5_real_orchestrator.py::TestTask2TavilyIntegration::test_web_search PASSED [ 39%]
tests/test_story_1_5_real_orchestrator.py::TestTask2TavilyIntegration::test_qna_search PASSED [ 43%]
tests/test_story_1_5_real_orchestrator.py::TestTask2TavilyIntegration::test_get_search_context PASSED [ 47%]
tests/test_story_1_5_real_orchestrator.py::TestTask2TavilyIntegration::test_extract_from_urls PASSED [ 52%]
tests/test_story_1_5_real_orchestrator.py::TestTask3OrchestratorCoordination::test_coordinate_research_github_only PASSED [ 56%]
tests/test_story_1_5_real_orchestrator.py::TestTask3OrchestratorCoordination::test_coordinate_research_web_only PASSED [ 60%]
tests/test_story_1_5_real_orchestrator.py::TestTask3OrchestratorCoordination::test_coordinate_research_both_sources PASSED [ 65%]
tests/test_story_1_5_real_orchestrator.py::TestTask3OrchestratorCoordination::test_delegate_to_agent PASSED [ 69%]
tests/test_story_1_5_real_orchestrator.py::TestTask3OrchestratorCoordination::test_get_available_tools PASSED [ 73%]
tests/test_story_1_5_real_orchestrator.py::TestTask4EndToEndIntegration::test_full_research_workflow PASSED [ 78%]
tests/test_story_1_5_real_orchestrator.py::TestTask4EndToEndIntegration::test_error_handling_invalid_repo PASSED [ 82%]
tests/test_story_1_5_real_orchestrator.py::TestTask4EndToEndIntegration::test_error_handling_uninitialized_client PASSED [ 86%]
tests/test_story_1_5_real_orchestrator.py::TestTask4EndToEndIntegration::test_performance_direct_vs_mcp PASSED [ 91%]
tests/test_story_1_5_real_orchestrator.py::TestTask4EndToEndIntegration::test_security_boundaries PASSED [ 95%]
tests/test_story_1_5_real_orchestrator.py::TestTask4EndToEndIntegration::test_rate_limit_awareness PASSED [100%]

============================= 23 passed in 38.76s =============================
