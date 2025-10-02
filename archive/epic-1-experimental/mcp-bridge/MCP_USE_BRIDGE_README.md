# MCP-Use Ollama Bridge - Single Source for MCP Loading

## Overview

`mcp_use_ollama_bridge.js` is the **single source** for dynamically loading MCP servers in the MADF project. It uses the mcp-use framework with local Ollama execution ($0 cost).

## Architecture

```
Python Agents → mcp_use_ollama_bridge.js → mcp-use → Ollama → MCP Servers
```

**Loaded Servers**: filesystem, tavily, context7
**Excluded**: serena, graphiti (loaded directly via Python MCP SDK in `src/core/mcp_bridge.py`)

## Usage

### From Command Line

```bash
# Structured input (recommended)
node mcp_use_ollama_bridge.js '["filesystem", "list_allowed_directories"]'
node mcp_use_ollama_bridge.js '["tavily", "search", {"query": "langgraph docs", "max_results": 3}]'

# Natural language (Ollama reasoning)
node mcp_use_ollama_bridge.js "Search the web for LangGraph tutorials"
```

### From Python Agents

```python
import subprocess
import json

# Call bridge from Python
result = subprocess.run(
    ['node', 'mcp_use_ollama_bridge.js',
     json.dumps(["tavily", "search", {"query": "langgraph multi-agent", "max_results": 3}])],
    capture_output=True,
    text=True
)

# Parse result
output = result.stdout
```

## Configuration

**Config File**: `mcp-use-ollama-config.json`

```json
{
  "llm": {
    "provider": "ollama",
    "model": "qwen2.5-mcp",
    "baseUrl": "http://localhost:11434"
  },
  "mcpServers": {
    "filesystem": { ... },
    "tavily": { ... },
    "context7": { ... }
  }
}
```

**Environment Variables** (in `.env`):
- `TAVILY_API_KEY` - Tavily web search API key
- `OPENAI_API_KEY` - Required for Context7 documentation

## Available MCP Servers

### 1. Filesystem MCP ✅
**Tools**: list_allowed_directories, read_file, write_file, search_files
**Performance**: ~2-3s per operation
**Test**: `node mcp_use_ollama_bridge.js '["filesystem", "list_allowed_directories"]'`

### 2. GitHub MCP
**Tools**: Repository operations, PR management, issue tracking, code quality
**Binary**: Official `github-mcp-server` from https://github.com/github/github-mcp-server/releases
**Installation**: Download binary and add to PATH
**API Key**: Required in `.env` as `GITHUB_API_KEY`
**Test**: `node mcp_use_ollama_bridge.js '["github", "get_user_info"]'`

### 3. Tavily MCP ✅
**Tools**: search (web search with sources)
**Performance**: ~60s (includes LangChain overhead)
**Test**: `node mcp_use_ollama_bridge.js '["tavily", "search", {"query": "test", "max_results": 1}]'`

### 4. Context7 MCP
**Tools**: resolve-library-id, get-docs
**Purpose**: Real-time documentation retrieval
**API Key**: Required in `.env` as `OPENAI_API_KEY`

## Prerequisites

1. **Node.js 20.x+**
2. **Ollama** installed and running (`http://localhost:11434`)
3. **qwen2.5-mcp model** created:
   ```bash
   "D:\Ollama\ollama.exe" create qwen2.5-mcp -f experimental/ollama_mcp_modelfile
   ```
4. **GitHub MCP Server Binary**:
   - Download from: https://github.com/github/github-mcp-server/releases
   - Add to PATH or place in project directory
   - Windows: `github-mcp-server.exe`
5. **Dependencies installed**:
   ```bash
   npm install mcp-use@^0.4.6 @langchain/ollama@^0.1.4 dotenv@^17.2.3
   ```

## Testing

```bash
# Test filesystem
node mcp_use_ollama_bridge.js '["filesystem", "list_allowed_directories"]'

# Test tavily
node mcp_use_ollama_bridge.js '["tavily", "search", {"query": "test", "max_results": 1}]'

# Test context7 (requires API key)
node mcp_use_ollama_bridge.js '["context7", "resolve-library-id", {"libraryName": "react"}]'
```

## Integration with Stories

### Story 1.2 (Analyst Agent)
- Uses **direct Serena MCP** (not this bridge)
- Uses **Context7 via this bridge** for documentation

### Story 1.3 (Knowledge Agent)
- Uses **direct Graphiti MCP** (not this bridge)
- Uses **Filesystem via this bridge** for file operations

### Story 1.5 (Orchestrator Agent)
- Uses **GitHub via this bridge** for repository operations
- Uses **Tavily via this bridge** for web research
- Uses **Filesystem via this bridge** for project files

## Performance

- **Startup**: ~5s (MCP server initialization)
- **Filesystem operations**: ~1s per call
- **Tavily search**: ~60s (9s actual search + 51s LangChain overhead)
- **Context7 docs**: ~3-5s per request

## Cost

**$0** - All operations use local Ollama model (qwen2.5-mcp), no external API calls to Claude/GPT.

## Troubleshooting

### "Ollama not running"
```bash
# Start Ollama
"D:\Ollama\ollama.exe" serve
```

### "Model qwen2.5-mcp not found"
```bash
"D:\Ollama\ollama.exe" create qwen2.5-mcp -f experimental/ollama_mcp_modelfile
```

### "Config file not found"
Ensure `mcp-use-ollama-config.json` exists in project root.

### Environment variables not loading
Check `.env` file exists and dotenv loads before MCPClient initialization.

## See Also

- **Full Handover Docs**: `experimental/MCP_USE_HYBRID_HANDOVER.md`
- **Python MCP Bridge**: `src/core/mcp_bridge.py` (for direct Serena/Graphiti)
- **Ollama Setup**: `README_OLLAMA_SETUP.md`