# Quick Start: mcp-use with Ollama

Modified `mcp-use` to use **local Ollama LLM** instead of Claude/OpenAI.

## Files Created

### 1. Configuration
**`mcp-use-ollama-config.json`** - Ollama LLM configuration for mcp-use
- Provider: Ollama (local)
- Model: qwen2.5:7b
- Base URL: http://localhost:11434
- Includes MCP server configs (filesystem, GitHub, Tavily)

### 2. Examples

**`mcp_ollama_example.js`** (Node.js)
- Uses `@langchain/ollama` with `mcp-use`
- Demonstrates MCPOrchestrator with local LLM
- Run: `node mcp_ollama_example.js`

**`mcp_ollama_python_example.py`** (Python)
- Uses `ollama` + `mcp` Python packages
- Alternative Python-based approach
- Run: `python mcp_ollama_python_example.py`

### 3. Documentation
**`docs/OLLAMA_MCP_SETUP.md`** - Complete setup guide
- Installation instructions
- Configuration examples
- Troubleshooting
- Performance comparison

## Quick Setup

### 1. Install Ollama (if not installed)
```bash
# Windows
winget install Ollama.Ollama

# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Function-Calling Model
```bash
# Recommended model (supports function calling)
ollama pull qwen2.5:7b

# Check installation
ollama list
```

### 3. Start Ollama Server
```bash
# Should already be running
# Check: http://localhost:11434
curl http://localhost:11434/api/tags
```

### 4. Install Node.js Dependencies (for mcp_ollama_example.js)
```bash
npm install mcp-use @langchain/ollama @langchain/core
```

### 5. Install Python Dependencies (for Python example)
```bash
pip install mcp ollama
```

## Running Examples

### Node.js Example
```bash
node mcp_ollama_example.js
```

Expected output:
```
🚀 Starting mcp-use with Ollama integration...
✅ Ollama LLM initialized (qwen2.5:7b)
✅ MCP Orchestrator created with 3 servers
✅ MCP servers initialized

📋 Available tools: 12
  - read_file: Read file contents
  - write_file: Write to file
  - list_directory: List directory contents
  ...

🤖 Running agent with Ollama...
📊 Agent Result: [...]
```

### Python Example
```bash
python mcp_ollama_python_example.py
```

Expected output:
```
🚀 Starting Ollama + MCP Integration
✅ Ollama running with 3 models
🔌 Connecting to filesystem MCP server...
✅ filesystem: 8 tools available
🤖 Ollama (qwen2.5:7b) processing: [...]
📊 Result: [...]
```

## Current Status

**Ollama Status**: ✅ Installed (`D:\Ollama\ollama.exe`)
**Process Running**: ✅ Yes (PID 26688)

### Next Steps to Test

1. **Start Ollama server explicitly** (if curl test fails):
   ```bash
   ollama serve
   ```

2. **Pull qwen2.5:7b model** (if not already installed):
   ```bash
   ollama pull qwen2.5:7b
   ```

3. **Test function calling**:
   ```bash
   curl http://localhost:11434/api/chat -d '{
     "model": "qwen2.5:7b",
     "messages": [{"role": "user", "content": "What is 2+2?"}],
     "tools": [{"type": "function", "function": {"name": "calculate", "description": "Calculate math"}}]
   }'
   ```

4. **Run Node.js example**:
   ```bash
   npm install mcp-use @langchain/ollama
   node mcp_ollama_example.js
   ```

## Key Configuration Changes

### Before (Cloud LLM)
```javascript
import { ChatAnthropic } from '@langchain/anthropic';

const llm = new ChatAnthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
  model: 'claude-3-5-sonnet-20241022'
});
```

### After (Local Ollama)
```javascript
import { ChatOllama } from '@langchain/ollama';

const llm = new ChatOllama({
  baseUrl: 'http://localhost:11434',
  model: 'qwen2.5:7b',  // Local model
  temperature: 0.7
});
```

## Benefits of Ollama

✅ **Free**: No API costs
✅ **Private**: Data stays local
✅ **Fast**: No network latency (with GPU)
✅ **Offline**: Works without internet
✅ **No Rate Limits**: Unlimited usage

## Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **qwen2.5:7b** | 4.7 GB | Fast | Excellent | General purpose (BEST) |
| llama3.1:8b | 4.9 GB | Fast | Good | Alternative |
| mistral:7b | 4.1 GB | Very Fast | Good | Speed-focused |

## Integration with MADF

Update `.env` to use Ollama:
```bash
# Add Ollama configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# Keep existing MCP server credentials
GITHUB_API_KEY=ghp_xxx
TAVILY_API_KEY=tvly_xxx
```

Update agent initialization in `src/agents/`:
```python
from langchain_ollama import ChatOllama

class AnalystAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
```

## Troubleshooting

**Issue**: curl returns empty response
**Fix**: Restart Ollama: `taskkill /F /IM ollama.exe && ollama serve`

**Issue**: Model not found
**Fix**: `ollama pull qwen2.5:7b`

**Issue**: Out of memory
**Fix**: Use smaller model: `ollama pull qwen2.5:3b`

## Documentation

Full documentation: `docs/OLLAMA_MCP_SETUP.md`