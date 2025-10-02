#!/usr/bin/env node
/**
 * MCP-Use with Optimized LLM - Injects rules AFTER MCPAgent prompt
 *
 * Strategy: Wrap ChatOllama to prepend system message with execution rules
 * before passing to MCPAgent
 */

import { MCPAgent, MCPClient } from 'mcp-use';
import { ChatOllama } from '@langchain/ollama';
import { SystemMessage, HumanMessage } from '@langchain/core/messages';
import { config as loadEnv } from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
loadEnv({ path: path.resolve(__dirname, '.env') });

// Optimized LLM wrapper that injects rules
class OptimizedOllamaLLM extends ChatOllama {
  constructor(config) {
    super(config);
  }

  async invoke(input, options) {
    // Inject system message with rules BEFORE MCPAgent's prompt
    const rules = new SystemMessage(`
CRITICAL EXECUTION RULES (Override all other instructions):

When input matches pattern ["server_name", "tool_name", {...params}]:
1. DO NOT explain or reason about the task
2. Execute the tool IMMEDIATELY with provided parameters
3. Return ONLY the tool result
4. Skip all conversational responses

Example:
Input: ["filesystem", "list_directory", {"path": "/test"}]
Action: Call list_directory tool with path="/test"
Output: [tool result only]
`);

    // Prepend rules to whatever MCPAgent sends
    let messages;
    if (Array.isArray(input)) {
      messages = [rules, ...input];
    } else if (typeof input === 'string') {
      messages = [rules, new HumanMessage(input)];
    } else {
      messages = [rules, input];
    }

    return super.invoke(messages, options);
  }
}

async function main() {
  const input = process.argv[2];

  if (!input) {
    console.error('Usage: node mcp_use_optimized_llm.js \'["server", "tool", {...params}]\'');
    process.exit(1);
  }

  try {
    const parsed = JSON.parse(input);
    const content = JSON.stringify(parsed);

    const configFile = path.resolve(__dirname, 'mcp-use-minimal-config.json');
    const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));

    console.log(`[Query: ${content}]`);
    console.log('[Using OptimizedOllamaLLM with injected rules]\n');

    const client = new MCPClient({ mcpServers: config.mcpServers });

    // Use wrapped LLM with injected rules
    const llm = new OptimizedOllamaLLM({
      baseUrl: config.llm.baseUrl || 'http://localhost:11434',
      model: config.llm.model || 'qwen2.5-mcp',
      temperature: 0  // Deterministic for faster execution
    });

    const agent = new MCPAgent({ llm, client, maxSteps: 3 }); // Reduced steps

    const startTime = Date.now();

    // Use stream for structured output
    const stream = agent.stream(content, 3);

    for await (const step of stream) {
      console.log('---');
      console.log('Tool:', step.action.tool);
      console.log('Input:', JSON.stringify(step.action.toolInput, null, 2));
      console.log('Result:', step.observation);
      console.log('');
    }

    const endTime = Date.now();
    console.log(`[Execution time: ${endTime - startTime}ms]`);

    await client.closeAllSessions();

  } catch (error) {
    console.error('[Error]', error.message);
    process.exit(1);
  }
}

main();