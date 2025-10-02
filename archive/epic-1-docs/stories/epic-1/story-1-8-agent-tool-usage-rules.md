# Story 1.8: Tool Efficiency Research for LangGraph Agents

As a **multiagent system developer**,
I want **BMAD agents to research and test optimal tools for LangGraph agents**,
so that **LangGraph agents use proven, efficient tools based on real test results**.

## Overview

BMAD agents will research, benchmark, and test available tools to determine which ones work best for each LangGraph agent's responsibilities. BMAD will run real tests, measure efficiency, and provide data-driven recommendations that LangGraph agents will implement.

**Architecture**:
- **BMAD agents** (PM, Dev, QA) = Research & testing team
- **LangGraph agents** (Orchestrator, Analyst, Knowledge, Developer, Validator) = Production implementation

## Objective

**BMAD-Driven Research**:
1. BMAD agents design test scenarios for each LangGraph agent
2. BMAD runs real tests comparing tool options (direct libraries vs MCP servers)
3. BMAD measures efficiency metrics (latency, tokens, accuracy, cost, reliability)
4. BMAD documents findings and recommendations
5. LangGraph agents implement optimal tools based on BMAD research

## Current State

### LangGraph Agents (Production - src/agents/)

1. **Orchestrator Agent** ([src/agents/orchestrator_agent.py](../../src/agents/orchestrator_agent.py))
   - Current tools: PyGithub (direct), tavily-python (direct)
   - Needs research: GitHub operations, web search, file operations

2. **Analyst Agent** ([src/agents/analyst_agent.py](../../src/agents/analyst_agent.py))
   - Current tools: Serena MCP (direct SDK)
   - Needs research: Code search, doc retrieval, reasoning tools

3. **Knowledge Agent** ([src/agents/knowledge_agent.py](../../src/agents/knowledge_agent.py))
   - Current tools: graphiti_core (direct library)
   - Needs research: Knowledge graphs, note management, file ops

4. **Developer Agent** ([src/agents/developer_agent.py](../../src/agents/developer_agent.py))
   - Current tools: None fully integrated
   - Needs research: Browser automation, debugging, file operations

5. **Validator Agent** ([src/agents/validator_agent.py](../../src/agents/validator_agent.py))
   - Current tools: DSPy (mentioned)
   - Needs research: Error tracking, DB optimization, test improvement

### Tool Options Available

**Direct Python Libraries** (~50 commonly used methods):
- PyGithub (20-25 methods) - Repository, PR, Issue operations
- tavily-python (4 methods) - search(), qna_search(), get_search_context(), extract()
- graphiti_core (5 methods) - add_episode(), search(), search_nodes(), search_facts()
- dspy-ai (5 modules) - Predict, ChainOfThought, ReAct, BootstrapFewShot
- psycopg (15 methods) - connect(), execute(), commit(), fetchone(), fetchall()

**MCP Servers** (~20-25 commonly used tools from 85 total):
- Serena MCP (10 tools) - read_file, search_for_pattern, get_symbols_overview, find_symbol
- Context7 MCP (2 tools) - resolve-library-id, get-library-docs
- Sequential Thinking MCP (1 tool) - sequentialthinking
- Filesystem MCP (6 tools) - read_text_file, write_file, edit_file, directory_tree
- Obsidian MCP (6 tools) - search, get_file_contents, create_file, patch_content
- Chrome DevTools MCP (6 tools) - new_page, navigate_to, take_snapshot, execute_javascript
- Sentry MCP (3 tools) - capture_error, list_issues, get_issue_details
- Postgres MCP Pro (4 tools) - execute_query, analyze_performance, get_schema

**Claude Code Built-in** (15 core + ~80 CLI = ~95 total):
- Core tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
- CLI tools: git, gh, npm, docker, pytest, etc.

**Total Commonly Used**: ~165 tools/methods (vs 390+ total available)

### BMAD Agents (Research Team)

1. **PM Agent (John)** ([.bmad-core/agents/pm.md](../../.bmad-core/agents/pm.md))
   - Role: Define research scope, test scenarios, success criteria
   - Tasks: Create test plans, document findings

2. **Dev Agent (James)** ([.bmad-core/agents/dev.md](../../.bmad-core/agents/dev.md))
   - Role: Implement test infrastructure, run benchmarks
   - Tasks: Build test framework, execute tests, collect metrics

3. **QA Agent** ([.bmad-core/agents/qa.md](../../.bmad-core/agents/qa.md))
   - Role: Validate test results, ensure quality
   - Tasks: Review test coverage, verify findings

## Task Breakdown

### Phase 1: Research Design (BMAD PM Agent - 2-3 hours)

**Task 1.1: Define Test Scenarios**
- [x] PM creates `docs/research/library-analysis/` (Direct Python Libraries)
  - [x] pygithub-common-methods.md (20-25 methods, HIGH priority)
  - [x] tavily-python-common-methods.md (4 methods, HIGH priority)
  - [x] graphiti-core-common-methods.md (5 methods, HIGH priority)
  - [x] dspy-common-modules.md (5 modules, MEDIUM priority)
  - [x] psycopg-common-methods.md (15 methods, HIGH priority)
- [x] PM creates `docs/research/mcp-analysis/` (MCP Servers)
  - [x] mcp-servers-common-tools.md (20-25 tools from 85 total)
- [ ] PM creates `docs/research/test-plan.md`
  - [ ] Function-level comparative tests (not tool-level)
  - [ ] Focus on 20-25 high-priority tools per category
  - [ ] Use case groupings (file ops, code search, web research)
  - [ ] Metrics: latency, token usage, accuracy, cost, reliability

**Task 1.2: Tool Options Analysis**
- [x] Research shows ~165 commonly used tools vs 390+ total
- [x] Direct Python libraries: ~50 methods (PyGithub, tavily, graphiti, DSPy, psycopg)
- [x] MCP servers: ~20-25 tools (Serena, Context7, Filesystem, Obsidian, Chrome DevTools)
- [x] Claude Code built-in: ~95 tools (Read, Write, Edit, Glob, Grep, Bash, git, gh, etc.)
- [ ] PM documents per-agent tool selection criteria
  - [ ] Orchestrator: PyGithub (18 methods), tavily-python (4 methods)
  - [ ] Analyst: Serena MCP (10 tools), Context7 MCP (2 tools)
  - [ ] Knowledge: graphiti_core (5 methods), Obsidian MCP (6 tools)
  - [ ] Developer: Chrome DevTools MCP (6 tools), Claude Code built-in
  - [ ] Validator: DSPy (5 modules), psycopg (15 methods), Sentry MCP (3 tools)

**Task 1.3: Benchmark Framework Design**
- [x] Research documents include performance characteristics per tool
- [ ] PM specifies function-level benchmark requirements in test plan
  - [ ] Latency measurement (p50, p90, p99) for common operations
  - [ ] Token usage tracking for API calls
  - [ ] Accuracy/quality scoring for search/analysis results
  - [ ] Cost estimation per 1000 operations
  - [ ] Reliability metrics (success rate, error types)

### Phase 2: Test Implementation (BMAD Dev Agent - 4-6 hours)

**Task 2.1: Build Test Infrastructure**
- [ ] Dev creates `tests/research/` directory structure
- [ ] Dev implements `tests/research/tool_benchmark.py`
  - [ ] `ToolBenchmark` class - Measure latency, tokens, success rate
  - [ ] `ComparisonRunner` class - A/B test tools
  - [ ] Metrics collection and logging
  - [ ] Results export (JSON/CSV)

**Task 2.2: Orchestrator Tool Tests**
- [ ] Dev creates `tests/research/test_orchestrator_tools.py`
  - [ ] **Test 1**: GitHub operations (focus on 5 HIGH priority methods)
    - PyGithub: get_repo(), get_contents(), create_pull(), list_issues(), search_repositories()
    - Measure latency, API rate limits, ease of use
  - [ ] **Test 2**: Web research (focus on 3 HIGH priority methods)
    - tavily-python: search(), qna_search(), get_search_context()
    - Measure search quality, speed, token usage, cost
  - [ ] **Test 3**: File operations (Claude Code vs Serena vs Filesystem MCP)
    - Read, Write, Edit, Glob, Grep (Claude Code built-in)
    - Serena: read_file, search_for_pattern, list_dir
    - Filesystem MCP: read_text_file, write_file, search_files
    - Measure performance for workflow coordination

**Task 2.3: Analyst Tool Tests**
- [ ] Dev creates `tests/research/test_analyst_tools.py`
  - [ ] **Test 1**: Serena MCP tool performance (10 HIGH priority tools)
    - LSP: get_symbols_overview, find_symbol, find_referencing_symbols, replace_symbol_body
    - File ops: read_file, search_for_pattern, list_dir
    - Memory: write_memory, read_memory
    - Shell: execute_shell_command
    - Measure accuracy, latency, token usage vs Claude Code alternatives
  - [ ] **Test 2**: Context7 MCP (2 tools)
    - resolve-library-id, get-library-docs
    - Compare vs docs-cache files and WebFetch
    - Measure freshness, speed, token usage
  - [ ] **Test 3**: Sequential Thinking MCP (1 tool)
    - sequentialthinking for complex multi-step analysis
    - Compare vs manual chain-of-thought
    - Measure quality, latency, token cost

**Task 2.4: Knowledge Tool Tests**
- [ ] Dev creates `tests/research/test_knowledge_tools.py`
  - [ ] **Test 1**: graphiti_core direct library (5 HIGH priority methods)
    - add_episode(), search(), search_nodes(), search_facts(), get_episode()
    - Validate "3x faster" claim from Story 1.3 vs MCP alternative
    - Measure latency, token usage, Neo4j performance
  - [ ] **Test 2**: Obsidian MCP (6 commonly used tools)
    - list_files_in_dir, get_file_contents, search, patch_content, append_content, create_file
    - Compare vs Claude Code file operations and Filesystem MCP
    - Test structured note management vs unstructured files
  - [ ] **Test 3**: Knowledge retrieval comparison
    - graphiti_core semantic search vs Obsidian keyword search vs Claude Code Grep
    - Test accuracy, speed, context quality for different query types

**Task 2.5: Developer Tool Tests**
- [ ] Dev creates `tests/research/test_developer_tools.py`
  - [ ] **Test 1**: Chrome DevTools MCP (6 commonly used tools)
    - new_page, navigate_to, take_snapshot, execute_javascript, list_console_messages, close_page
    - Measure browser automation reliability, latency, features
    - Story 1.6 validation: end-to-end workflow testing
  - [ ] **Test 2**: File operations for code generation
    - Claude Code Write, Edit vs Filesystem MCP vs Serena file ops
    - Test code generation workflow: create file, edit file, validate syntax
    - Measure speed, accuracy, error handling
  - [ ] **Test 3**: Debugging and inspection
    - Chrome DevTools console capture vs manual logging
    - DOM snapshot quality vs manual inspection
    - Measure error detection capability, detail level

**Task 2.6: Validator Tool Tests**
- [ ] Dev creates `tests/research/test_validator_tools.py`
  - [ ] **Test 1**: DSPy modules (5 commonly used)
    - Predict, ChainOfThought, ReAct, BootstrapFewShot, Evaluate
    - Test self-improvement workflow: compile optimizer, run examples, measure accuracy gain
    - Measure optimization latency, quality improvement, token cost
  - [ ] **Test 2**: psycopg direct library (15 HIGH priority methods)
    - connect(), execute(), commit(), fetchone(), fetchall(), executemany(), copy(), rollback()
    - Compare vs Postgres MCP Pro for query performance analysis
    - Measure speed, connection pooling, bulk operations
  - [ ] **Test 3**: Sentry MCP (3 commonly used tools)
    - capture_error, list_issues, get_issue_details
    - Compare vs Python logging, sentry-sdk direct library
    - Measure error capture detail, aggregation, real-time tracking

**Task 2.7: Execute All Tests**
- [ ] Dev creates `tests/research/run_all_research.py` - Master test runner
- [ ] Dev runs all benchmark tests
- [ ] Dev collects results in `tests/research/results/` directory

### Phase 3: Analysis & Documentation (BMAD PM + QA - 3-4 hours)

**Task 3.1: QA Validates Results**
- [ ] QA reviews all test results for consistency
- [ ] QA verifies test coverage (min 3 scenarios per agent)
- [ ] QA validates metric collection accuracy
- [ ] QA documents any test anomalies

**Task 3.2: PM Analyzes Findings**
- [ ] PM creates `docs/research/tool-efficiency-analysis.md`
  - [ ] Aggregate results from all tests
  - [ ] Calculate averages: latency, tokens, cost, accuracy
  - [ ] Identify clear winners for specific scenarios
  - [ ] Document trade-offs (speed vs accuracy vs cost)
  - [ ] Include data visualizations (tables, charts)

**Task 3.3: PM Documents Recommendations**
- [ ] PM creates `docs/research/tool-recommendations.md`
  - [ ] **Orchestrator recommendations**:
    - When to use PyGithub vs GitHub MCP
    - When to use tavily-python vs Tavily MCP
    - File operation recommendations
  - [ ] **Analyst recommendations**:
    - When to use Serena MCP vs filesystem
    - When to use Context7 MCP
    - Sequential Thinking use cases
  - [ ] **Knowledge recommendations**:
    - graphiti_core vs Graphiti MCP decision tree
    - Obsidian MCP vs Filesystem MCP for notes
  - [ ] **Developer recommendations**:
    - Chrome DevTools vs Playwright selection
  - [ ] **Validator recommendations**:
    - Sentry MCP integration guidance
    - Postgres MCP vs direct connection
    - DSPy optimization strategies

**Task 3.4: PM Creates Implementation Guide**
- [ ] PM creates `docs/research/implementation-guide.md`
  - [ ] Step-by-step for LangGraph agents to adopt recommended tools
  - [ ] Code examples for each integration pattern
  - [ ] Migration path from current tools
  - [ ] Performance expectations based on test data

### Phase 4: LangGraph Implementation (Future Story)

**Note**: Implementation in LangGraph agents will be separate story
- [ ] LangGraph agents adopt recommended tools
- [ ] Update agent code based on BMAD findings
- [ ] Production validation of BMAD recommendations

## Testing Strategy

### Test Execution by BMAD Dev

1. **Benchmark Metrics Collection**
   - Latency: Time to first response, total execution time, p50/p90/p99
   - Token Usage: Input tokens, output tokens, cost estimate
   - Accuracy: Task completion rate, error rate, quality score
   - Cost: API costs, infrastructure costs, cost per 1000 ops
   - Reliability: Success rate, error types, fallback behavior

2. **Test Scenarios Per Agent**

| LangGraph Agent | Test Scenarios | Tools to Compare | BMAD Tester |
|----------------|---------------|------------------|-------------|
| Orchestrator | GitHub search, PR listing, web research | PyGithub vs GitHub MCP, tavily vs Tavily MCP | Dev Agent |
| Analyst | Semantic search, doc retrieval, reasoning | Serena vs filesystem, Context7, Sequential Thinking | Dev Agent |
| Knowledge | Episode storage, knowledge search, notes | graphiti_core vs Graphiti MCP, Obsidian vs filesystem | Dev Agent |
| Developer | Browser automation, DOM inspection, debugging | Chrome DevTools vs Playwright | Dev Agent |
| Validator | Error tracking, query optimization, test improvement | Sentry vs logging, Postgres MCP vs direct, DSPy | Dev Agent |

3. **QA Validation**
   - Verify test results consistency
   - Validate metric accuracy
   - Ensure minimum test coverage
   - Document edge cases

## Deliverables

### Research Documentation (by BMAD PM)
1. `docs/research/test-plan.md` - Test scenarios and success criteria
2. `docs/research/tool-options.md` - Tool comparison matrix
3. `docs/research/tool-efficiency-analysis.md` - Aggregated findings with data
4. `docs/research/tool-recommendations.md` - Specific recommendations per agent
5. `docs/research/implementation-guide.md` - How LangGraph agents adopt tools

### Test Infrastructure (by BMAD Dev)
1. `tests/research/tool_benchmark.py` - Benchmark framework
2. `tests/research/test_orchestrator_tools.py` - Orchestrator tests
3. `tests/research/test_analyst_tools.py` - Analyst tests
4. `tests/research/test_knowledge_tools.py` - Knowledge tests
5. `tests/research/test_developer_tools.py` - Developer tests
6. `tests/research/test_validator_tools.py` - Validator tests
7. `tests/research/run_all_research.py` - Master test runner
8. `tests/research/results/` - Test results (JSON/CSV)

### QA Validation (by BMAD QA)
1. Test coverage report
2. Results validation report
3. Anomaly documentation

## Success Criteria

**BMAD Research Complete**:
- [ ] PM defines test plan with scenarios for all 5 LangGraph agents
- [ ] Dev implements test infrastructure and runs all benchmarks
- [ ] Minimum 3 test scenarios per LangGraph agent executed
- [ ] Quantitative metrics collected (latency, tokens, accuracy, cost, reliability)
- [ ] QA validates all test results
- [ ] PM documents findings with data visualizations
- [ ] PM provides clear tool recommendations per LangGraph agent
- [ ] Implementation guide created for LangGraph agent updates

**Research Quality**:
- [ ] All tests run on real tool integrations (no mocks)
- [ ] Results are reproducible
- [ ] Recommendations backed by measured data
- [ ] Trade-offs clearly documented

## Dependencies

**LangGraph Agents** (research subjects):
- Story 1.1 (COMPLETED) - 5-agent architecture
- Story 1.2 (COMPLETED) - Serena MCP (Analyst)
- Story 1.3 (COMPLETED) - Graphiti (Knowledge)
- Story 1.4 (IN PROGRESS) - Validator infrastructure
- Story 1.5 (IN PROGRESS) - Orchestrator tools
- Story 1.6 (COMPLETED) - Chrome DevTools (Developer)

**Documentation**:
- LangGraph docs ([.claude/docs-cache/langgraph-docs.md](../../.claude/docs-cache/langgraph-docs.md))
- MCP server docs ([.claude/docs-cache/](../../.claude/docs-cache/) - all mcp-*.md files)

**BMAD Agents**:
- PM agent (research design)
- Dev agent (test implementation)
- QA agent (validation)

## Estimated Effort

**Total**: 6-9 hours (BMAD agents) - Reduced by 33% due to focused scope
- Phase 1 (PM): 1-2 hours - Research design (documentation analysis complete)
- Phase 2 (Dev): 3-4 hours - Test implementation and execution (focused on ~165 commonly used tools)
- Phase 3 (PM + QA): 2-3 hours - Analysis and documentation
- Phase 4: Future story (LangGraph implementation)

**Scope Reduction Rationale**:
- Research already completed for ~50 direct library methods and ~20-25 MCP tools
- Focus on function-level tests (not tool-level) reduces test matrix by 80%
- High-priority tools identified, eliminating over-engineering with uncommon tools

## Notes

### Division of Labor

**BMAD Agents** (Research Team):
- **PM (John)**: Design test plan, analyze findings, document recommendations
- **Dev (James)**: Build test infrastructure, run benchmarks, collect data
- **QA**: Validate results, ensure quality, verify coverage

**LangGraph Agents** (Production System):
- Receive recommendations from BMAD research
- Implement optimal tools in future story
- No research responsibilities

### Research Philosophy

- **Empirical Testing**: BMAD runs real tests, not assumptions
- **Data-Driven**: All recommendations backed by measured metrics
- **Practical Trade-offs**: Document speed vs accuracy vs cost
- **Production Ready**: Test with actual MCP integrations and libraries

### Integration with LangGraph

From [LangGraph docs](../../.claude/docs-cache/langgraph-docs.md):
- Tool calling via chat models
- MCP integration via `langchain-mcp-adapters`
- Custom tool creation
- LangSmith evaluations for performance tracking

### Key Research Questions

BMAD will answer through testing:
1. **Direct vs MCP**: When is direct library faster/better than MCP wrapper?
2. **Latency Trade-offs**: How much latency for better accuracy?
3. **Token Efficiency**: Which tools minimize tokens without quality loss?
4. **Reliability**: Which tools have best error handling?
5. **Cost**: Total cost per 1000 operations for each tool?

## Follow-up Tasks

1. **Story 1.9**: LangGraph agents implement BMAD recommendations
2. **Continuous Monitoring**: Set up automated tool performance tracking
3. **LangSmith Integration**: Production performance validation
4. **Tool Updates**: Re-test when new MCP servers or libraries available

## Related Documents

- [LangGraph Tools](../../.claude/docs-cache/langgraph-docs.md) - Tool calling patterns
- [MCP Servers](../../.claude/docs-cache/) - All mcp-*.md documentation
- [Tech Stack](../../architecture/3-tech-stack.md) - Current tool selections
- [Story 1.3](story-1-3-graphiti-mcp-obsidian-filesystem.md) - Initial performance data
- [BMAD PM Agent](../../.bmad-core/agents/pm.md) - Research lead
- [BMAD Dev Agent](../../.bmad-core/agents/dev.md) - Test implementation
- [BMAD QA Agent](../../.bmad-core/agents/qa.md) - Validation
