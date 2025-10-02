#!/usr/bin/env node
/**
 * MCP-Use Direct Tool Executor
 *
 * Executes MCP tools directly without LLM agent reasoning.
 * Returns raw tool results for programmatic use.
 *
 * USAGE:
 *   node mcp_use_direct_tool.js <server> <tool> <json_params>
 *
 * EXAMPLES:
 *   node mcp_use_direct_tool.js filesystem list_allowed_directories '{}'
 *   node mcp_use_direct_tool.js filesystem search_files '{"path":"D:/dev/MADF","pattern":"*.md"}'
 *   node mcp_use_direct_tool.js tavily search '{"query":"test","max_results":1}'
 */

import { MCPClient } from 'mcp-use';
import { config as loadEnv } from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
loadEnv({ path: path.resolve(__dirname, '.env') });

async function main() {
  const [server, tool, paramsJson] = process.argv.slice(2);

  if (!server || !tool) {
    console.error('Usage: node mcp_use_direct_tool.js <server> <tool> <json_params>');
    console.error('Example: node mcp_use_direct_tool.js filesystem list_directory \'{"path":"D:/dev/MADF"}\'');
    process.exit(1);
  }

  let params = {};
  if (paramsJson) {
    try {
      params = JSON.parse(paramsJson);
    } catch (error) {
      console.error('Invalid JSON params:', error.message);
      process.exit(1);
    }
  }

  try {
    // Load minimal config (filesystem only for testing)
    const configFile = path.resolve(__dirname, 'mcp-use-minimal-config.json');

    if (!fs.existsSync(configFile)) {
      console.error(`Config file not found: ${configFile}`);
      process.exit(1);
    }

    const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));

    console.log(`[Connecting to ${server} MCP server...]`);

    // Create MCP client WITHOUT agent
    const client = new MCPClient({ mcpServers: config.mcpServers });

    // Get available tools
    const tools = await client.getTools();
    console.log(`[Found ${tools.length} tools]`);

    // Find the specific tool
    const toolName = `${server}-${tool}`;
    const targetTool = tools.find(t => t.name === toolName || t.name === tool);

    if (!targetTool) {
      console.error(`Tool not found: ${toolName}`);
      console.error(`Available tools: ${tools.map(t => t.name).join(', ')}`);
      process.exit(1);
    }

    console.log(`[Executing: ${targetTool.name}]`);
    console.log(`[Parameters: ${JSON.stringify(params)}]`);

    // Call tool directly
    const result = await client.callTool(targetTool.name, params);

    // Output raw result
    console.log('\n[RESULT]');
    console.log(JSON.stringify(result, null, 2));

    // Cleanup
    await client.closeAllSessions();

  } catch (error) {
    console.error('[ERROR]', error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

main();