#!/usr/bin/env node
/**
 * MCP-Use Ollama Bridge: Single Source for MCP Tool Loading
 *
 * Loads all MCP servers dynamically via mcp-use framework with Ollama LLM.
 * Excludes direct MCP integrations (Serena, Graphiti) which are loaded natively in Python.
 *
 * USAGE:
 * 1. Via structured input (pre-translated):
 *    node mcp_use_ollama_bridge.js '["filesystem", "list_allowed_directories"]'
 *
 * 2. Via natural language (Ollama reasoning):
 *    node mcp_use_ollama_bridge.js "List all allowed directories"
 *
 * LOADED MCP SERVERS: filesystem, github, tavily, context7
 * EXCLUDED: serena, graphiti (direct Python integration)
 *
 * PREREQUISITES:
 * - Download github-mcp-server binary from https://github.com/github/github-mcp-server/releases
 * - Add to PATH or place in project directory
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
loadEnv({ path: path.resolve(__dirname, '.env') });

async function main() {
  const input = process.argv[2];

  if (!input) {
    console.error("Usage: node mcp_use_ollama_bridge.js '<translated-array-or-natural-language>'");
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

    // Use unified config file from project root
    const configFile = path.resolve(__dirname, 'mcp-use-ollama-config.json');

    if (!fs.existsSync(configFile)) {
      console.error(`[Error] Config file not found: ${configFile}`);
      process.exit(1);
    }

    const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));

    console.log(`[Using config: ${configFile}]`);

    // Create MCP client with server configurations
    const client = new MCPClient({ mcpServers: config.mcpServers });

    // Initialize custom Ollama model with embedded conditional rules
    const llm = new ChatOllama({
      baseUrl: config.llm.baseUrl || 'http://localhost:11434',
      model: config.llm.model || 'qwen2.5-mcp'
    });

    // Create agent with client and LLM
    const agent = new MCPAgent({
      llm: llm,
      client: client,
      maxSteps: 10
    });

    console.log(`[Ollama Executing with ${config.llm.model}]\n`);

    const result = await agent.run(content, 10);

    console.log('\n[Result]');
    console.log(result);

  } catch (error) {
    console.error('[Error]', error.message);
    process.exit(1);
  }
}

main();