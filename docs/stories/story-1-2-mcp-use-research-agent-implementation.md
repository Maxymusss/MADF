# Story 1.2: MCP-use Research Agent Implementation

**Epic:** Multi-Agent Financial Research Framework
**Story ID:** 1.2
**Priority:** High
**Estimated Effort:** 8-12 hours (Day 2 morning)

## User Story

As a **financial research system operator**,
I want **research agents that access real-time financial data through multiple MCP servers using mcp-use library**,
so that **market intelligence reports contain current, accurate information from diverse sources**.

## Story Context

**Existing System Integration:**
- Integrates with: Product Manager agent (Story 1.1), MCP server infrastructure
- Technology: Python async/asyncio, mcp-use library, LangChain Anthropic (Sonnet)
- Follows pattern: Agent communication via JSON messages established in Story 1.1
- Touch points: File-based communication protocol, financial MCP servers

## Acceptance Criteria

**Functional Requirements:**
1. Research agent uses async Python implementation with mcp-use library for multi-server configuration
2. Agent integrates LangChain Anthropic (Sonnet) for cost-effective tool calling capabilities
3. Agent implements multi-server configuration accessing Yahoo Finance, Google News via dedicated MCP servers
4. Agent implements time filtering with "This week" = Monday 8 days before ask-date including weekends
5. Agent focuses exclusively on Asia/G10 currencies and interest rate markets using targeted MCP server queries
6. Agent maintains individual error logs for learning system development
7. Agent communicates with Product Manager through established JSON message format while using mcp-use for data access

**Integration Requirements:**
8. mcp-use agent Python environment integrates cleanly with existing Node.js MADF infrastructure
9. Agent MCP server connections use dedicated configurations that do not conflict with Claude Code MCP setup
10. Agent resource usage (Python + async operations) stays within 20% memory increase limit established in NFR1

**Quality Requirements:**
11. Change is covered by appropriate tests
12. Documentation is updated for research agent configuration
13. No regression in existing functionality verified

## Technical Notes

- **Integration Approach:** Separate Python environment using mcp-use library for MCP server access
- **Existing Pattern Reference:** JSON communication protocol from Story 1.1
- **Key Constraints:** Memory usage limits, cost optimization with Sonnet model, async performance

## Definition of Done

- [ ] Research agent implemented with async Python and mcp-use library
- [ ] LangChain Anthropic (Sonnet) integration functional
- [ ] Multi-server MCP configuration working (Yahoo Finance, Google News)
- [ ] Time filtering logic implemented correctly
- [ ] Asia/G10 market focus filtering working
- [ ] Individual error logging functional
- [ ] JSON communication with Product Manager working
- [ ] Python environment integration with Node.js verified
- [ ] Dedicated MCP configurations not conflicting with Claude Code
- [ ] Memory usage within 20% increase limit confirmed
- [ ] Documentation updated
- [ ] Tests pass (existing and new)

## Risk Assessment

**Primary Risk:** mcp-use library complexity with async operations and multi-server setup
**Mitigation:** Start with single MCP server, expand to multi-server gradually
**Rollback:** Remove Python research agent components, maintain file-based communication structure

## Dependencies

- Story 1.1: Product Manager Agent Foundation (JSON communication protocol)
- Story 1.3: Financial Data Source MCP Server Configuration (parallel development)

## Technical Dependencies

- mcp-use library
- LangChain Anthropic integration
- Python async/asyncio environment
- Financial MCP servers (Yahoo Finance, Google News)