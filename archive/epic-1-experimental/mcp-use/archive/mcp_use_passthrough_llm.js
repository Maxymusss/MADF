#!/usr/bin/env node
/**
 * MCP-Use Pass-Through LLM - Skip reasoning for structured inputs
 *
 * Uses Claude 3.5 Haiku (agent-trained model) instead of Qwen2.5-mcp
 * Tests if Context7 completes properly with agent-capable LLM
 */

import { MCPAgent, MCPClient } from 'mcp-use';
import { ChatAnthropic } from '@langchain/anthropic';
import { SystemMessage, HumanMessage, AIMessage } from '@langchain/core/messages';
import { config as loadEnv } from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
loadEnv({ path: path.resolve(__dirname, '.env') });

// Pass-through LLM: Forces immediate tool execution without reasoning
class PassThroughLLM extends ChatAnthropic {
  constructor(config, toolSchemas = null) {
    super(config);
    this.toolSchemas = toolSchemas;
  }

  // Pre-validation: Pass through tool names as-is
  validateToolCall(serverName, toolName, params) {
    // No manual mappings - let MCP handle tool resolution
    return {
      canonicalName: toolName,
      validatedParams: { ...params }
    };
  }

  async invoke(input, options) {
    // Claude is agent-trained, doesn't need pass-through override
    // Just use normal ChatAnthropic behavior
    return super.invoke(input, options);
  }
}

async function main() {
  const input = process.argv[2];

  if (!input) {
    console.error('Usage: node mcp_use_passthrough_llm.js \'["server", "tool", {...params}]\'');
    process.exit(1);
  }

  try {
    let content;

    // Try parsing as JSON first
    try {
      const parsed = JSON.parse(input);

      // Pre-validate and auto-correct tool calls
      if (Array.isArray(parsed) && parsed.length >= 3) {
        const [serverName, toolName, params] = parsed;

        // Apply auto-corrections
        const tempLLM = new PassThroughLLM({});
        const validated = tempLLM.validateToolCall(serverName, toolName, params);

        // Update parsed array with corrected values
        parsed[1] = validated.canonicalName;
        parsed[2] = validated.validatedParams;
      }

      content = JSON.stringify(parsed);
    } catch (parseError) {
      // Not JSON, treat as natural language
      content = input;
    }

    const configFile = path.resolve(__dirname, 'mcp-use-ollama-config.json');
    const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));

    console.log(`[Query: ${content}]`);
    console.log('[Using PassThroughLLM - forcing direct tool execution]\n');

    const client = new MCPClient({ mcpServers: config.mcpServers });

    // Use pass-through LLM with Claude
    const llm = new PassThroughLLM({
      model: 'claude-3-5-haiku-20241022',  // Fast, cheap Claude model
      temperature: 0,  // Zero creativity = faster
      apiKey: process.env.ANTHROPIC_API_KEY
    });

    const agent = new MCPAgent({ llm, client, maxSteps: 2 }); // Minimal steps

    const startTime = Date.now();

    // Use run() for direct execution - passthrough LLM should complete in 1-2 steps
    console.log('[Executing tool call...]\n');
    const result = await agent.run(content, 2);

    const endTime = Date.now();

    console.log('\n[Result]');
    console.log(result);
    console.log(`\n[Execution time: ${endTime - startTime}ms]`);

    await client.closeAllSessions();

  } catch (error) {
    console.error('[Error]', error.message);
    if (error.stack) console.error(error.stack);
    process.exit(1);
  }
}

main();