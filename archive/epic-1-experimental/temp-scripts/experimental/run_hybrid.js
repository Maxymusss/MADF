#!/usr/bin/env node
/**
 * Hybrid Mode Runner: Claude Code Translation + Ollama Execution
 * Standalone - doesn't affect existing mcp_ollama_example.js
 *
 * USAGE:
 * 1. Via direct translated input (Claude Code pre-translates):
 *    node run_hybrid.js '["filesystem", "list_allowed_directories"]'
 *
 * 2. Via natural language (Ollama reasons with embedded rules):
 *    node run_hybrid.js "List all allowed directories"
 */

import { MCPAgent, MCPClient } from 'mcp-use';
import { ChatOllama } from '@langchain/ollama';
import { config as loadEnv } from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Load .env from project root
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
loadEnv({ path: path.resolve(__dirname, '../.env') });

async function main() {
  const input = process.argv[2];

  if (!input) {
    console.error("Usage: node run_hybrid.js '<translated-array-or-natural-language>'");
    process.exit(1);
  }

  try {
    // Parse input: could be JSON array or natural language string
    let content;
    try {
      const parsed = JSON.parse(input);
      if (Array.isArray(parsed) && parsed.length >= 2) {
        content = JSON.stringify(parsed);
        console.log(`[Structured] ${content}`);
      } else {
        content = input;
        console.log(`[Natural Language] ${content}`);
      }
    } catch {
      content = input;
      console.log(`[Natural Language] ${content}`);
    }

    const configFile = fs.existsSync('./config_tavily_only.json')
      ? './config_tavily_only.json'
      : fs.existsSync('./config_github_only.json')
      ? './config_github_only.json'
      : fs.existsSync('./config_filesystem_only.json')
      ? './config_filesystem_only.json'
      : './config_hybrid.json';

    const config = JSON.parse(
      fs.readFileSync(configFile, 'utf-8')
    );

    console.log(`[Using config: ${configFile}]`);

    // Create MCP client with server configurations
    const client = new MCPClient({ mcpServers: config.mcpServers });

    // Initialize custom Ollama model with embedded conditional rules
    const llm = new ChatOllama({
      baseUrl: 'http://localhost:11434',
      model: 'qwen2.5-mcp'
    });

    // Create agent with client and LLM
    const agent = new MCPAgent({
      llm: llm,
      client: client,
      maxSteps: 10
    });

    console.log(`[Ollama Executing with qwen2.5-mcp]\n`);

    const result = await agent.run(content, 10);

    console.log('\n[Result]');
    console.log(result);

  } catch (error) {
    console.error('[Error]', error.message);
    process.exit(1);
  }
}

main();