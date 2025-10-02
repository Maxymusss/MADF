#!/usr/bin/env node
/**
 * MCP-Use Stream Tool Executor
 *
 * Uses stream() method to get structured tool results without conversational overhead.
 * Better for programmatic use than run() which adds LLM reasoning.
 *
 * USAGE:
 *   node mcp_use_stream_tool.js '["filesystem", "list_allowed_directories"]'
 */

import { MCPAgent, MCPClient } from 'mcp-use';
import { ChatOllama } from '@langchain/ollama';
import { config as loadEnv } from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
loadEnv({ path: path.resolve(__dirname, '.env') });

async function main() {
  const input = process.argv[2];

  if (!input) {
    console.error('Usage: node mcp_use_stream_tool.js \'["server", "tool", {...params}]\'');
    process.exit(1);
  }

  try {
    const parsed = JSON.parse(input);
    const content = JSON.stringify(parsed);

    const configFile = path.resolve(__dirname, 'mcp-use-minimal-config.json');
    const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));

    console.log(`[Query: ${content}]`);

    const client = new MCPClient({ mcpServers: config.mcpServers });
    const llm = new ChatOllama({
      baseUrl: config.llm.baseUrl || 'http://localhost:11434',
      model: config.llm.model || 'qwen2.5-mcp'
    });

    const agent = new MCPAgent({ llm, client, maxSteps: 5 });

    console.log('[Using stream() method for structured output]\n');

    // Use stream() instead of run() - yields intermediate steps
    const stream = agent.stream(content, 5);

    for await (const step of stream) {
      console.log('---');
      console.log('Tool:', step.action.tool);
      console.log('Input:', JSON.stringify(step.action.toolInput, null, 2));
      console.log('Result:', step.observation);
      console.log('');
    }

    await client.closeAllSessions();

  } catch (error) {
    console.error('[Error]', error.message);
    process.exit(1);
  }
}

main();