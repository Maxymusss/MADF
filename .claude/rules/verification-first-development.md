# Verification-First Development Rules

**CRITICAL**: Apply systematic verification over assumption-driven development:

## Core Principles

1. **"Verify First, Document Second"** - Test any technical claim before building documentation/code around it. Never assume functionality - validate it.

2. **"Challenge Assumptions at Category Boundaries"** - When creating lists/categories, explicitly verify each item belongs where you think. Don't mix conceptual dimensions (importance ≠ loading requirements).

3. **"Question Inheritance"** - Before copying patterns/lists to new files, verify the source is correct. Break assumption cascades before they propagate.

## Implementation Requirements

### Framework Integration Standards
- **CRITICAL: Verify Return Types**: Never assume framework return types match input types
  - **LangGraph Workflows**: Return dicts, not Pydantic objects (use `result["key"]` not `result.key`)
  - **Context Managers**: Check if methods return managers vs direct objects (`SqliteSaver.from_conn_string()`)
  - **Async Compatibility**: Match async/sync patterns throughout execution stack
  - **Testing Protocol**: Write explicit tests for framework return types and behavior
  - **Documentation Check**: Always verify latest API documentation before integration

### Diagnostic & Troubleshooting Protocol
**MANDATORY SEQUENCE**: When debugging configuration, connection, or environment issues:

1. **ALWAYS check configuration files FIRST** before making assumptions
   - Read .env files, config.json, package.json, etc.
   - Verify actual values, not just command outputs that might show unexpanded variables
2. **THEN check runtime state** (processes, connections, environment in current session)
3. **THEN attempt fixes** based on actual evidence, not assumptions

**CRITICAL**: Never conclude "X is missing" without directly reading the source configuration file where X should be defined.
**Example**: If environment variables appear unset in shell output, read .env file before concluding they're missing.

## Quality Gates & TDD Approach
- **Mandatory TDD**: All non-trivial tasks require tests first
- **Logical Correctness**: Especially critical for financial/market calculations in alphaseek
- **Human Review Points**: Architecture decisions, security changes, production deployments