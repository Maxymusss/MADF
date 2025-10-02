# MCP API Key Troubleshooting Guide

## Issue: Invalid API Key Errors

When MCP servers fail with "Invalid API key" errors, use this guide to diagnose and fix.

## Quick Fix: Use Minimal Config

**Problem**: Third-party API keys (Tavily, Context7) may be expired/invalid
**Solution**: Use minimal config with only filesystem (no external APIs)

```bash
# Copy minimal config to main config
cp mcp-use-minimal-config.json mcp-use-ollama-config.json

# Test with filesystem only
node mcp_use_ollama_bridge.js '["filesystem", "list_allowed_directories"]'
```

## API Key Verification

### 1. Tavily API Key
**Error**: `MCP error -32603: Invalid API key`
**Location**: `.env` line 30: `TAVILY_API_KEY=tvly-dev-...`

**Verify**:
```bash
curl -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -d '{"api_key":"YOUR_KEY","query":"test","max_results":1}'
```

**Get New Key**: https://tavily.com/ (free tier available)

### 2. Context7 API Key
**Error**: Context7 requires OpenAI API key
**Location**: `.env` line 4: `OPENAI_API_KEY=sk-proj-...`

**Verify**:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

**Get New Key**: https://platform.openai.com/api-keys

### 3. GitHub Token
**Location**: `.env` line 12: `GITHUB_API_KEY=ghp_...`

**Verify**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.github.com/user
```

**Get New Token**: https://github.com/settings/tokens (needs `repo` scope)

## Handling Strategy Options

### Option 1: Skip Optional MCPs (Recommended)
Use minimal config with only essential servers (filesystem).

**Pros**: Always works, no external dependencies
**Cons**: Limited functionality

### Option 2: Fix API Keys
Update `.env` with valid keys from respective platforms.

**Pros**: Full functionality
**Cons**: Requires accounts/subscriptions

### Option 3: Graceful Fallback (Future)
Implement try-catch logic in bridge to skip failed servers.

**Implementation**:
```javascript
// Future enhancement for mcp_use_ollama_bridge.js
const availableServers = {};
for (const [name, config] of Object.entries(allServers)) {
  try {
    await testConnection(name, config);
    availableServers[name] = config;
  } catch (error) {
    console.warn(`Skipping ${name}: ${error.message}`);
  }
}
```

## Configuration Files

### Full Config (requires all API keys)
**File**: `mcp-use-ollama-config.json`
**Servers**: filesystem, github, tavily, context7
**Use when**: All API keys are valid

### Minimal Config (no external APIs)
**File**: `mcp-use-minimal-config.json`
**Servers**: filesystem only
**Use when**: Testing or API keys unavailable

### Custom Config
Create your own with only available servers:
```json
{
  "llm": {...},
  "mcpServers": {
    "filesystem": {...},
    "github": {...}  // Only add if binary installed and token valid
  }
}
```

## Test Each Server Individually

```bash
# Test filesystem (always works)
node mcp_use_ollama_bridge.js '["filesystem", "list_allowed_directories"]'

# Test tavily (requires valid API key)
node mcp_use_ollama_bridge.js '["tavily", "search", {"query": "test", "max_results": 1}]'

# Test context7 (requires OpenAI key)
node mcp_use_ollama_bridge.js '["context7", "resolve-library-id", {"libraryName": "react"}]'

# Test github (requires binary + token)
node mcp_use_ollama_bridge.js '["github", "get_user_info"]'
```

## Current Status

✅ **Filesystem**: Working (no API key needed)
⚠️ **Tavily**: API key invalid/expired
⚠️ **Context7**: Requires OpenAI API key validation
❌ **GitHub**: Binary not installed

## Recommended Action

**For immediate use**:
```bash
# Use minimal config (filesystem only)
cp mcp-use-minimal-config.json mcp-use-ollama-config.json
node mcp_use_ollama_bridge.js '["filesystem", "list_allowed_directories"]'
```

**For full functionality**:
1. Get new Tavily API key from https://tavily.com/
2. Validate OpenAI API key at https://platform.openai.com/
3. Download GitHub MCP binary from https://github.com/github/github-mcp-server/releases
4. Update `.env` with valid keys
5. Restore full config from backup or experimental/config_hybrid.json