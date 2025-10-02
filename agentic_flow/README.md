# Epic 2 - Agentic Flow Framework

**LangGraph + LangSmith Fork with Claude SDK Integration**

## Overview

This directory contains the Epic 2 greenfield implementation - a fork-based approach to building a production-grade multi-agent framework.

## Architecture

- **Forks**: LangGraph, LangSmith, langgraph-checkpoint-postgres (removing LangChain dependencies)
- **Agents**: 5 specialized agents (Orchestrator, Analyst, Knowledge, Developer, Validator)
- **Tools**: Custom tools salvaged from Epic 1 (Graphiti, DSPy, Sentry, Postgres)
- **MCP**: Native MCP integration via Claude SDK
- **State**: Pydantic V2 state models

## Salvaged from Epic 1

- Agent patterns and tool assignments
- MCP server configurations
- Direct library integrations
- Test scenarios and NO MOCKS philosophy

## Epic 2 Stories (8-week timeline)

### Week 1-2: Fork & Cleanup
- Fork LangGraph, LangSmith, checkpoints
- Remove all LangChain dependencies
- Verify 90%+ tests passing

### Week 3-4: Claude SDK Integration
- Add Claude SDK instrumentation to LangSmith
- Build ClaudeTracer (replace LangChainTracer)
- Implement MCPRegistry for tool integration

### Week 5-6: Agent Migration
- Migrate 5 agents to forked LangGraph
- Port state models from Epic 1
- Integrate MCP tools

### Week 7-8: Testing & Validation
- Port Epic 1 test scenarios
- Create datasets from traces
- Run evaluations and A/B tests
- Measure performance vs Epic 1

## Success Criteria

- All 3 forks functional with 0 LangChain dependencies
- 5 agents operational with Claude SDK
- LangSmith self-improvement workflow working
- Performance ≥ Epic 1 baseline
