# MCP-Use Directory

All mcp-use related files organized here.

## Priority Order (Use This)

### PRIMARY (Use First)
**mapping_mcp_bridge.js** - Intelligent MCP bridge with auto-strategy selection
- Auto-selects best query strategy per tool using calibrated mappings
- 3-tier approach: Tool mapping → Parameter analysis → Fallback chain
- Uses mcp-strategy-mapping.json for proven strategies
- Fastest and most reliable option

### SECONDARY (Fallback)
**mcp_use_ollama_bridge.js** - Baseline bridge with standard Ollama agent
- Simple natural language → tool execution
- Uses Ollama for all reasoning (slower)
- Good for testing/debugging

### LEGACY (Archive)
- mcp_use_stream_tool.js (old recommendation)
- mcp_use_passthrough_llm.js (experimental)
- mcp_use_optimized_llm.js (minimal gains)

## Configuration
- **mcp-use-ollama-config.json** - Unified config for all servers
- **mcp-strategy-mapping.json** - Tool → strategy calibration data
- mcp-use-minimal-config.json (filesystem only, testing)

## Usage

### Recommended: mapping_mcp_bridge.js
```bash
# Uses calibrated strategy for filesystem tools
node mcp-use/mapping_mcp_bridge.js '["filesystem", "list_directory", {"path": "/project"}]'

# Auto-detects Context7 needs imperative strategy
node mcp-use/mapping_mcp_bridge.js '["context7", "resolve-library-id", {"libraryName": "react"}]'

# Falls back to parameter analysis if tool not in mapping
node mcp-use/mapping_mcp_bridge.js '["new_tool", "action", {"param": "value"}]'
```

### Fallback: mcp_use_ollama_bridge.js
```bash
# Natural language (slower)
node mcp-use/mcp_use_ollama_bridge.js "List the directory contents"

# Structured input
node mcp-use/mcp_use_ollama_bridge.js '["filesystem", "list_directory", {"path": "/project"}]'
```

## Test Scripts
- test_ollama_rules.js
- test_system_prompt_injection.js
- demo_context7_mcp_use.py
- test_mcp_use_tavily.py
- comprehensive_calibration.js (strategy testing)

## Documentation
- MCP_USE_BRIDGE_README.md (main guide)
- MCP_USE_OPTIMIZED_SOLUTION.md (stream optimization)
- PASSTHROUGH_OPTIMIZATION_RESULTS.md (pass-through strategy)
- RULE_INJECTION_RESULTS.md (first optimization attempt)
- OLLAMA_RULES_ANALYSIS.md (why modelfile rules don't work)
- FILESYSTEM_MCP_TEST_RESULTS.md (function testing)
- MCP_API_KEY_TROUBLESHOOTING.md (API key verification)
- CONTEXT7_INTEGRATION_FINDINGS.md (Context7 integration notes)

