#!/usr/bin/env node
/**
 * Minimal MCP test - filesystem only
 */
import { MCPAgent, MCPClient } from 'mcp-use';
import { ChatOllama } from '@langchain/ollama';

async function main() {
  console.log('[START] Minimal MCP test\n');

  try {
    // Single filesystem server only
    const client = new MCPClient({
      mcpServers: {
        filesystem: {
          command: 'npx',
          args: ['-y', '@modelcontextprotocol/server-filesystem', 'D:/dev/MADF'],
          env: { ALLOWED_DIRECTORIES: 'D:/dev/MADF' }
        }
      }
    });

    console.log('[OK] MCPClient created');

    const llm = new ChatOllama({
      baseUrl: 'http://localhost:11434',
      model: 'qwen2.5-mcp'
    });

    console.log('[OK] Ollama LLM created');

    const agent = new MCPAgent({
      llm: llm,
      client: client,
      maxSteps: 3
    });

    console.log('[OK] MCPAgent created\n');
    console.log('[RUN] Asking simple question...\n');

    const result = await agent.run('What is 2 + 2?', 3);

    console.log('\n[RESULT]', result);

    await client.cleanup();
    console.log('\n[OK] Cleanup complete');

  } catch (error) {
    console.error('\n[FAIL]', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

main();