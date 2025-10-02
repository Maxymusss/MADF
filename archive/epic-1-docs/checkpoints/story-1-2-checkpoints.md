# Story 1.2: MCP-use Research Agent Implementation - Checkpoints

**Status:** NOT STARTED
**Priority:** High (Day 2 morning)
**Estimated Effort:** 8-12 hours
**Dependencies:** Story 1.1 ✓ COMPLETE

## Checkpoint Overview

| Checkpoint | Status | Requirements | Expected Verification |
|------------|---------|-------------|---------------------|
| CP2.1 - mcp-use Library Setup | ⏳ PENDING | async Python, mcp-use install | Library imports, basic connection |
| CP2.2 - LangChain Integration | ⏳ PENDING | Sonnet model, cost optimization | Tool calling capabilities test |
| CP2.3 - Multi-Server MCP Config | ⏳ PENDING | Yahoo Finance, Google News servers | Server connectivity, data retrieval |
| CP2.4 - Time Filtering Logic | ⏳ PENDING | "This week" = Monday 8 days before | Date range validation tests |
| CP2.5 - Market Focus Filtering | ⏳ PENDING | Asia/G10 currencies, interest rates | Geographic/market type filtering |
| CP2.6 - Error Logging System | ⏳ PENDING | Individual agent error tracking | Error capture, log file creation |
| CP2.7 - JSON Communication | ⏳ PENDING | Product Manager protocol integration | Message format compatibility |
| CP2.8 - Environment Integration | ⏳ PENDING | Python + Node.js coexistence | Memory usage, performance validation |

## Detailed Checkpoints

### CP2.1 - mcp-use Library Setup
- **Status:** ⏳ PENDING
- **Requirements:**
  - [ ] Install mcp-use library in dedicated Python environment
  - [ ] Configure async Python implementation
  - [ ] Verify library imports and basic functionality
  - [ ] Test connection capabilities to MCP servers
- **Expected Files:** `requirements_mcp.txt`, `langgraph_core/agents/research.py`
- **Verification:** Basic mcp-use import and connection test
- **Risk:** mcp-use library compatibility with existing asyncio setup

### CP2.2 - LangChain Anthropic (Sonnet) Integration
- **Status:** ⏳ PENDING
- **Requirements:**
  - [ ] Integrate LangChain Anthropic with Sonnet model
  - [ ] Configure cost-effective tool calling capabilities
  - [ ] Implement async LangChain agent wrapper
  - [ ] Test model response quality vs cost optimization
- **Expected Files:** `langgraph_core/integrations/langchain_anthropic.py`
- **Verification:** Sonnet model calls, tool usage, cost tracking
- **Risk:** Cost optimization vs research quality balance

### CP2.3 - Multi-Server MCP Configuration
- **Status:** ⏳ PENDING
- **Dependencies:** Story 1.3 (parallel development)
- **Requirements:**
  - [ ] Configure Yahoo Finance MCP server connection
  - [ ] Configure Google News MCP server connection
  - [ ] Implement multi-server query coordination
  - [ ] Ensure MCP configs don't conflict with Claude Code setup
- **Expected Files:** `mcp-configs/research-agent.json`, server connection modules
- **Verification:** Successful data retrieval from both servers
- **Risk:** MCP server configuration conflicts, connection stability

### CP2.4 - Time Filtering Logic Implementation
- **Status:** ⏳ PENDING
- **Requirements:**
  - [ ] Implement "This week" = Monday 8 days before ask-date logic
  - [ ] Include weekends in time range calculation
  - [ ] Handle timezone considerations for global markets
  - [ ] Validate date range accuracy
- **Expected Files:** `langgraph_core/utils/time_filtering.py`
- **Verification:** Date range calculation tests, timezone handling
- **Risk:** Timezone complexity, weekend handling edge cases

### CP2.5 - Asia/G10 Market Focus Filtering
- **Status:** ⏳ PENDING
- **Requirements:**
  - [ ] Define geographic coverage: CN, TW, KR, HK, SG, TH, MY, PH, ID, IN, US
  - [ ] Implement currency market filtering (FX pairs)
  - [ ] Implement interest rate market filtering
  - [ ] Create targeted MCP server query templates
- **Expected Files:** `langgraph_core/config/market_definitions.py`
- **Verification:** Market filtering accuracy, query targeting tests
- **Risk:** Market definition completeness, query efficiency

### CP2.6 - Individual Error Logging System
- **Status:** ⏳ PENDING
- **Requirements:**
  - [ ] Implement agent-specific error logging
  - [ ] Create structured error capture for learning system
  - [ ] Log MCP server connection errors
  - [ ] Log data processing errors with context
- **Expected Files:** `langgraph_core/utils/error_logging.py`, log file structure
- **Verification:** Error capture tests, log file creation
- **Risk:** Log file management, error classification accuracy

### CP2.7 - JSON Communication Protocol
- **Status:** ⏳ PENDING
- **Dependencies:** Story 1.1 JSON format ✓
- **Requirements:**
  - [ ] Implement JSON message parsing from Product Manager
  - [ ] Create JSON response format for research results
  - [ ] Maintain compatibility with existing communication protocol
  - [ ] Handle message validation and error responses
- **Expected Files:** `langgraph_core/communication/json_protocol.py`
- **Verification:** Message format compatibility tests with Story 1.1
- **Risk:** Protocol compatibility, message validation complexity

### CP2.8 - Python/Node.js Environment Integration
- **Status:** ⏳ PENDING
- **Requirements:**
  - [ ] Verify Python research agent integration with Node.js MADF
  - [ ] Ensure memory usage stays within 20% increase limit (NFR1)
  - [ ] Test async operations performance
  - [ ] Validate clean environment separation
- **Expected Files:** Environment configuration, monitoring scripts
- **Verification:** Memory usage tests, performance benchmarks
- **Risk:** Memory consumption, async coordination complexity

## Pre-Implementation Analysis

### Technical Architecture Decisions Required:
1. **mcp-use Library:** Async implementation approach, error handling strategy
2. **Multi-Server Coordination:** Connection pooling, failover mechanisms
3. **Cost Optimization:** Sonnet model usage patterns, caching strategies
4. **Environment Isolation:** Python/Node.js boundary management

### Integration Points with Story 1.1:
- JSON communication protocol (established)
- WorkflowState compatibility
- Product Manager agent coordination
- Error handling consistency

### Parallel Development with Story 1.3:
- MCP server configurations shared
- Financial data source definitions aligned
- Server connection testing coordinated

## Definition of Done Checklist
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

## Risk Mitigation Strategy
**Primary Risk:** mcp-use library complexity with async operations and multi-server setup
**Mitigation Plan:**
1. Start with single MCP server (Yahoo Finance)
2. Validate async operations with basic queries
3. Expand to multi-server configuration incrementally
4. Implement comprehensive error handling early
**Rollback Plan:** Remove Python research agent components, maintain file-based communication structure

## Success Metrics
- All 8 checkpoints verified
- Memory usage increase < 20%
- Research data retrieval < 5s per query
- Error logging capture rate > 95%
- JSON protocol compatibility maintained