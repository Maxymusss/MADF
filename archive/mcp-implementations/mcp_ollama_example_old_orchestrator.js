#!/usr/bin/env node
/**
 * mcp-use with Ollama Local LLM Example
 *
 * Demonstrates using mcp-use with Ollama instead of Claude/OpenAI
 * Requires: npm install mcp-use @langchain/ollama
 */

import { MCPOrchestrator } from 'mcp-use';
import { ChatOllama } from '@langchain/ollama';

async function main() {
  console.log('🚀 Starting mcp-use with Ollama integration...\n');

  // 1. Initialize Ollama LLM (using LangChain.js)
  const llm = new ChatOllama({
    baseUrl: 'http://localhost:11434',
    model: 'qwen2.5:7b', // Use any Ollama model that supports function calling
    temperature: 0.7,
    maxTokens: 4096,
  });

  console.log('✅ Ollama LLM initialized (qwen2.5:7b)');

  // 2. Create MCP Orchestrator with Ollama
  const orchestrator = new MCPOrchestrator({
    llm: llm,
    servers: {
      // Filesystem MCP Server
      filesystem: {
        command: 'npx',
        args: [
          '-y',
          '@modelcontextprotocol/server-filesystem',
          process.cwd()
        ],
        env: {
          ALLOWED_DIRECTORIES: process.cwd()
        }
      },

      // GitHub MCP Server
      github: {
        command: 'npx',
        args: ['-y', '@gongrzhe/server-github'],
        env: {
          GITHUB_TOKEN: process.env.GITHUB_API_KEY
        }
      },

      // Tavily Web Search MCP Server
      tavily: {
        command: 'npx',
        args: ['-y', 'tavily-mcp'],
        env: {
          TAVILY_API_KEY: process.env.TAVILY_API_KEY
        }
      }
    },
    options: {
      verbose: true,
      timeout: 60000
    }
  });

  console.log('✅ MCP Orchestrator created with 3 servers\n');

  // 3. Initialize MCP servers
  await orchestrator.initialize();
  console.log('✅ MCP servers initialized\n');

  // 4. List available tools
  const tools = await orchestrator.listTools();
  console.log(`📋 Available tools: ${tools.length}`);
  tools.forEach(tool => {
    console.log(`  - ${tool.name}: ${tool.description}`);
  });
  console.log();

  // 5. Execute agent task using local Ollama LLM
  console.log('🤖 Running agent with Ollama...\n');

  const result = await orchestrator.runAgent({
    messages: [
      {
        role: 'user',
        content: 'Search the web for "LangGraph multi-agent systems" and summarize the top 3 results'
      }
    ],
    maxIterations: 5
  });

  console.log('📊 Agent Result:');
  console.log(JSON.stringify(result, null, 2));

  // 6. Cleanup
  await orchestrator.cleanup();
  console.log('\n✅ Cleanup complete');
}

// Run with error handling
main().catch(error => {
  console.error('❌ Error:', error.message);
  console.error(error.stack);
  process.exit(1);
});