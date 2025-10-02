# Ollama + MCP Integration Guide

Configure `mcp-use` and MCP servers to use **Ollama local LLM** instead of Claude/OpenAI.

## Prerequisites

### 1. Install Ollama

**Windows:**
```bash
# Download from https://ollama.com/download
# Or use winget
winget install Ollama.Ollama
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Ollama Model

Pull a model that **supports function calling** (required for MCP tool use):

```bash
# Recommended: Qwen 2.5 (7B) - Good balance of speed and capability
ollama pull qwen2.5:7b

# Alternatives:
ollama pull llama3.1:8b      # Meta's Llama 3.1
ollama pull mistral:7b       # Mistral 7B
ollama pull deepseek-r1:7b   # DeepSeek (reasoning model)
```

⚠️ **Important**: Not all models support function calling. Qwen 2.5, Llama 3.1, and Mistral are verified to work.

### 3. Start Ollama Server

```bash
# Start Ollama server (default: http://localhost:11434)
ollama serve
```

Verify it's running:
```bash
curl http://localhost:11434/api/tags
```

## Configuration

### Option 1: Node.js with mcp-use (Recommended)

#### Install Dependencies
```bash
npm install mcp-use @langchain/ollama @langchain/core
```

#### Configuration File
Create `mcp-use-ollama-config.json`:

```json
{
  "llm": {
    "provider": "ollama",
    "model": "qwen2.5:7b",
    "baseUrl": "http://localhost:11434",
    "temperature": 0.7,
    "maxTokens": 4096
  },
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": {
        "ALLOWED_DIRECTORIES": "."
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@gongrzhe/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_API_KEY}"
      }
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp"],
      "env": {
        "TAVILY_API_KEY": "${TAVILY_API_KEY}"
      }
    }
  }
}
```

#### Example Code
See `mcp_ollama_example.js`:

```javascript
import { MCPOrchestrator } from 'mcp-use';
import { ChatOllama } from '@langchain/ollama';

// Initialize Ollama LLM
const llm = new ChatOllama({
  baseUrl: 'http://localhost:11434',
  model: 'qwen2.5:7b',
  temperature: 0.7,
  maxTokens: 4096,
});

// Create orchestrator with Ollama
const orchestrator = new MCPOrchestrator({
  llm: llm,
  servers: { /* MCP server configs */ }
});

await orchestrator.initialize();

// Run agent with local LLM
const result = await orchestrator.runAgent({
  messages: [{ role: 'user', content: 'Your task here' }],
  maxIterations: 5
});
```

#### Run
```bash
node mcp_ollama_example.js
```

### Option 2: Python with MCP SDK

#### Install Dependencies
```bash
pip install mcp ollama
```

#### Example Code
See `mcp_ollama_python_example.py`:

```python
import ollama
from mcp.client import ClientSession

class OllamaMCPClient:
    def __init__(self, model="qwen2.5:7b"):
        self.model = model
        self.ollama_client = ollama.Client()

    def chat_with_tools(self, prompt, tools):
        response = self.ollama_client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            tools=tools
        )
        return response["message"]["content"]
```

#### Run
```bash
python mcp_ollama_python_example.py
```

## Environment Setup

Create `.env` file with MCP server credentials:

```bash
# GitHub MCP
GITHUB_API_KEY=ghp_your_token_here

# Tavily Web Search MCP
TAVILY_API_KEY=tvly-your_api_key_here

# Context7 Documentation MCP (requires OpenAI for embeddings)
OPENAI_API_KEY=sk-proj-your_key_here

# Ollama server (if not localhost)
OLLAMA_BASE_URL=http://localhost:11434
```

## Testing Ollama Function Calling

Test if your Ollama model supports function calling:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:7b",
  "messages": [
    {
      "role": "user",
      "content": "What is the weather like in Paris?"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get weather for a city",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "City name"
            }
          },
          "required": ["city"]
        }
      }
    }
  ]
}'
```

Expected response should include `tool_calls` field.

## Supported MCP Servers with Ollama

| MCP Server | Works with Ollama | Notes |
|------------|-------------------|-------|
| **filesystem** | ✅ Yes | File operations (read, write, list) |
| **github** | ✅ Yes | Repository management, PR creation |
| **tavily** | ✅ Yes | Web search and research |
| **context7** | ⚠️ Partial | Requires OpenAI for embeddings |
| **sequential-thinking** | ⚠️ Partial | Works but reasoning quality varies |
| **obsidian** | ✅ Yes | Note management |
| **postgres** | ✅ Yes | Database operations |
| **sentry** | ✅ Yes | Error tracking |

## Performance Considerations

### Model Selection

| Model | Size | Speed | Tool Calling | Recommended |
|-------|------|-------|--------------|-------------|
| **qwen2.5:7b** | 4.7 GB | Fast | ✅ Excellent | **Best overall** |
| **llama3.1:8b** | 4.9 GB | Fast | ✅ Good | Good alternative |
| **mistral:7b** | 4.1 GB | Very Fast | ✅ Good | Fastest option |
| **deepseek-r1:7b** | 4.7 GB | Medium | ❌ Limited | Not recommended |

### Hardware Requirements

**Minimum:**
- RAM: 8 GB (for 7B models)
- CPU: Modern multi-core processor
- Disk: 10 GB free space

**Recommended:**
- RAM: 16 GB+
- GPU: NVIDIA GPU with 8GB+ VRAM (optional, but 10x faster)
- Disk: SSD with 20 GB+ free space

### GPU Acceleration

If you have NVIDIA GPU:

```bash
# Check GPU support
ollama list

# Models automatically use GPU if available
# Verify GPU usage:
nvidia-smi

# Force CPU-only mode (if needed)
CUDA_VISIBLE_DEVICES="" ollama serve
```

## Troubleshooting

### Issue: "Ollama not running"

**Solution:**
```bash
# Start Ollama server
ollama serve

# Or as background service (Linux/Mac)
ollama serve &
```

### Issue: "Model doesn't support function calling"

**Solution:**
```bash
# Pull a function-calling compatible model
ollama pull qwen2.5:7b
```

### Issue: "Connection refused to localhost:11434"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve
```

### Issue: "Out of memory"

**Solution:**
```bash
# Use smaller model
ollama pull qwen2.5:3b

# Or increase system swap/pagefile
```

### Issue: "Tools not being called"

**Solution:**
- Ensure model supports function calling
- Verify tool schema format matches Ollama expectations
- Check Ollama logs: `journalctl -u ollama -f` (Linux)

## Comparison: Ollama vs Cloud LLMs

| Feature | Ollama (Local) | Claude/OpenAI (Cloud) |
|---------|----------------|----------------------|
| **Cost** | Free | $$$$ Pay per token |
| **Privacy** | 100% Private | Data sent to cloud |
| **Speed** | Fast (with GPU) | Network dependent |
| **Quality** | Good (7B-70B) | Excellent |
| **Setup** | Medium | Easy |
| **Offline** | ✅ Yes | ❌ No |
| **Rate Limits** | ❌ None | ✅ Yes |

## Best Practices

1. **Use GPU if available**: 10x speed improvement
2. **Start with qwen2.5:7b**: Best balance of quality and speed
3. **Monitor memory**: Larger models require more RAM
4. **Keep Ollama updated**: `ollama --version` and check releases
5. **Test tool calling**: Verify model supports function calling before production use

## Integration with MADF Project

Update agent configurations to use Ollama:

### AnalystAgent with Ollama
```python
# src/agents/analyst_agent.py
from langchain_ollama import ChatOllama

class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__("Analyst", "Code Analysis Specialist")
        self.llm = ChatOllama(
            model="qwen2.5:7b",
            base_url="http://localhost:11434"
        )
```

### OrchestratorAgent with Ollama
```python
# src/agents/orchestrator_agent.py
async def initialize_with_ollama(self):
    """Initialize with local Ollama LLM"""
    from langchain_ollama import ChatOllama

    self.llm = ChatOllama(
        model="qwen2.5:7b",
        base_url="http://localhost:11434",
        temperature=0.7
    )
```

## Next Steps

1. ✅ Install Ollama and pull `qwen2.5:7b`
2. ✅ Test function calling with curl
3. ✅ Run `mcp_ollama_example.js` or `mcp_ollama_python_example.py`
4. ✅ Integrate Ollama into MADF agents
5. ✅ Run Story 1.1 tests with Ollama LLM

## Resources

- **Ollama Documentation**: https://ollama.com/docs
- **mcp-use Documentation**: https://docs.mcp-use.io
- **LangChain Ollama**: https://js.langchain.com/docs/integrations/chat/ollama
- **MCP Specification**: https://modelcontextprotocol.io

## Support

Questions or issues? Check:
- Ollama Discord: https://discord.gg/ollama
- MCP Community: https://discord.gg/modelcontextprotocol
- MADF Issues: `D:\dev\MADF\.bmad-core\rules\`