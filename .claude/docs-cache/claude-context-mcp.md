# Claude Context MCP Server Documentation

## Overview
Claude Context is an MCP (Model Context Protocol) plugin that enables semantic code search for AI coding agents like Claude Code.

## Key Features
- Semantic code search across entire codebases
- Efficient vector database indexing
- Hybrid search combining BM25 and dense vector techniques
- Supports multiple AI coding platforms and tools
- Reduces token usage by ~40% while maintaining high-quality code retrieval

## Prerequisites
1. **Node.js** version 20.0.0 to < 24.0.0
2. **OpenAI API key** for embedding
3. **Zilliz Cloud API key** for vector database

## Installation
**NPM Package**: `@zilliz/claude-context-mcp`

### Basic Installation Command
```bash
claude mcp add claude-context \
-e OPENAI_API_KEY=sk-your-openai-api-key \
-e MILVUS_TOKEN=your-zilliz-cloud-api-key \
-- npx @zilliz/claude-context-mcp@latest
```

## Configuration
Add to `.mcp.json`:
```json
{
  "claude-context": {
    "command": "npx",
    "args": ["-y", "@zilliz/claude-context-mcp@latest"],
    "env": {
      "OPENAI_API_KEY": "sk-your-openai-api-key",
      "MILVUS_TOKEN": "your-zilliz-cloud-api-key"
    }
  }
}
```

## Setup Steps
1. Sign up for Zilliz Cloud to get a vector database API key
2. Get an OpenAI API key for embedding
3. Configure the MCP server using the command above
4. Index your codebase using the `index_codebase` tool
5. Start searching code with natural language queries

## Usage
- Index codebase: Use `index_codebase` tool
- Search code: Natural language queries for semantic code search
- Supports multiple AI coding platforms: Claude Code, Cursor, VS Code

## Benefits
- Cost-effective for large codebases
- High-quality code retrieval
- Significant token usage reduction (~40%)
- Semantic understanding of code context

## GitHub Repository
https://github.com/zilliztech/claude-context