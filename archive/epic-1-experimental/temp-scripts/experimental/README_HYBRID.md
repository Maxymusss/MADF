# Hybrid Mode: Claude Code + Ollama

Parallel implementation - does NOT affect existing Ollama-only setup.

## Architecture

```
User Prompt
    ↓
Claude Code (native reasoning - no external API)
    ↓
Structured Format: ["server", "tool"] or ["server", "tool", {...}] or "string"
    ↓
run_hybrid.js
    ↓
mcp-use → Ollama (qwen2.5-mcp with embedded rules)
    ↓
MCP Servers
```

**Key Insight**: Claude Code already runs Sonnet 4.5, so translation happens natively without external API calls.

## Setup

```bash
cd experimental

# Install Node.js dependencies
npm install mcp-use @langchain/ollama @langchain/core

# Pull base model and create custom model
ollama pull qwen2.5:7b
ollama create qwen2.5-mcp -f ollama_mcp_modelfile
```

## Usage

**Option 1: Direct structured input (Claude Code pre-translates)**
```bash
# 2-element array (simple tool, no args)
node run_hybrid.js '["filesystem", "list_allowed_directories"]'

# 3-element array (tool with args)
node run_hybrid.js '["github", "search_repositories", {"query": "langgraph"}]'
```

**Option 2: Natural language (Ollama reasons with embedded rules)**
```bash
node run_hybrid.js "List all allowed directories"
```

## Workflow Integration

When working with Claude Code:
1. User provides natural language prompt
2. Claude Code translates to structured format: `["server", "tool"]` or `["server", "tool", {...args}]`
3. Claude Code calls `run_hybrid.js` with translated input
4. Ollama (qwen2.5-mcp) executes based on embedded rules

## Models

- **qwen2.5:7b** - Base model (existing setup uses this)
- **qwen2.5-mcp** - Custom model with embedded conditional rules (hybrid mode)

## Conditional Rules (Embedded in qwen2.5-mcp)

**RULE 1**: Array `["server", "tool"]` → Execute immediately, no args
**RULE 2**: Array `["server", "tool", {...}]` → Execute with args immediately
**RULE 3**: String `"natural language"` → Reason and decide tools
**RULE 4**: Invalid format → Return error

## Files

- `ollama_mcp_modelfile` - Custom Ollama model definition with embedded rules
- `run_hybrid.js` - Main runner (accepts pre-translated or natural language input)
- `config_hybrid.json` - MCP server configuration
- `setup_hybrid.sh` - One-time setup script (reference)

## Environment Variables

```bash
# MCP servers only (no Anthropic key needed - Claude Code already runs locally)
GITHUB_API_KEY=ghp_xxx
TAVILY_API_KEY=tvly_xxx
```

## Comparison with Current Setup

| Feature | Current (Ollama Only) | Hybrid (This) |
|---------|----------------------|---------------|
| Entry | `mcp_ollama_example.js` | `run_hybrid.js` |
| Model | `qwen2.5:7b` | `qwen2.5-mcp` |
| Translation | None | Claude Code (native) |
| Execution | Ollama | Ollama |
| Cost | $0 | $0 (no external API) |
| Reasoning | Ollama | Claude Code + Ollama |

## Testing

Verify custom model works:
```bash
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"qwen2.5-mcp","prompt":"What is 2+2?","stream":false}'
```

Expected response includes `"response":"4"`

## Status

- [x] Custom Ollama model created (qwen2.5-mcp)
- [x] Architecture revised (removed external API dependency)
- [x] run_hybrid.js accepts pre-translated input
- [x] Ollama model verified working
- [ ] MCP server connection timing optimization (in progress)

## Notes

- No external API costs - Claude Code already runs Sonnet 4.5 locally
- Parallel to existing setup - no conflicts
- Custom model embeds conditional rules as default system prompt
- Easy rollback to Ollama-only if needed