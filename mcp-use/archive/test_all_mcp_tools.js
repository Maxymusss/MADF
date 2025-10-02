#!/usr/bin/env node
/**
 * Test all MCP tools with qwen3-coder:480b-cloud
 * Measures execution time for each tool
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

const configFile = path.resolve(__dirname, 'mcp-use-ollama-config.json');
const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));

// Test cases for each MCP tool
const TEST_CASES = [
  // Filesystem MCP
  { name: 'list_allowed_directories', query: 'List all allowed directories' },
  { name: 'list_directory', query: 'List files in D:/dev/MADF' },
  { name: 'read_text_file', query: 'Read the file D:/dev/MADF/package.json' },
  { name: 'get_file_info', query: 'Get metadata for D:/dev/MADF/package.json' },
  { name: 'directory_tree', query: 'Show directory tree for D:/dev/MADF/mcp-use (max depth 2)' },
  { name: 'search_files', query: 'Search for files matching *.md in D:/dev/MADF/docs' },

  // Tavily MCP
  { name: 'tavily-search', query: 'Search web for "LangChain agents tutorial" using tavily-search' },
  { name: 'tavily-extract', query: 'Extract content from https://example.com using tavily-extract' },

  // Context7 MCP
  { name: 'resolve-library-id', query: 'Find library ID for Next.js using resolve-library-id' },
  { name: 'get-library-docs', query: 'Get documentation for /vercel/next.js using get-library-docs with 2000 tokens' }
];

async function testTool(testCase, agent) {
  console.log(`\n[${'='.repeat(60)}]`);
  console.log(`Testing: ${testCase.name}`);
  console.log(`Query: ${testCase.query}`);
  console.log(`[${'='.repeat(60)}]`);

  const startTime = Date.now();

  try {
    const result = await agent.run(testCase.query, 5);
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);

    console.log(`\n[Result]`);
    console.log(result.substring(0, 500) + (result.length > 500 ? '...' : ''));
    console.log(`\n[Duration: ${duration}s] ✅ SUCCESS`);

    return { tool: testCase.name, duration: parseFloat(duration), status: 'success' };
  } catch (error) {
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);

    console.log(`\n[Error] ${error.message}`);
    console.log(`[Duration: ${duration}s] ❌ FAILED`);

    return { tool: testCase.name, duration: parseFloat(duration), status: 'failed', error: error.message };
  }
}

async function main() {
  console.log(`${'='.repeat(70)}`);
  console.log('MCP Tool Performance Test - qwen3-coder:480b-cloud');
  console.log(`${'='.repeat(70)}`);
  console.log(`Config: ${configFile}`);
  console.log(`Model: ${config.llm.model}`);
  console.log(`Total tests: ${TEST_CASES.length}`);
  console.log(`${'='.repeat(70)}\n`);

  const client = new MCPClient({ mcpServers: config.mcpServers });

  const llm = new ChatOllama({
    baseUrl: config.llm.baseUrl || 'http://localhost:11434',
    model: config.llm.model || 'qwen3-coder:480b-cloud',
    temperature: 0
  });

  const agent = new MCPAgent({ llm, client, maxSteps: 5 });

  const results = [];

  for (const testCase of TEST_CASES) {
    const result = await testTool(testCase, agent);
    results.push(result);

    // Brief pause between tests
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  await client.closeAllSessions();

  // Summary
  console.log(`\n\n${'='.repeat(70)}`);
  console.log('SUMMARY');
  console.log(`${'='.repeat(70)}\n`);

  const successCount = results.filter(r => r.status === 'success').length;
  const failCount = results.filter(r => r.status === 'failed').length;
  const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);

  console.log(`Total tests: ${results.length}`);
  console.log(`Success: ${successCount} ✅`);
  console.log(`Failed: ${failCount} ❌`);
  console.log(`Total execution time: ${totalDuration.toFixed(2)}s`);
  console.log(`Average per tool: ${(totalDuration / results.length).toFixed(2)}s\n`);

  console.log('Detailed Results:');
  console.log(`${'='.repeat(70)}`);
  console.log(`${'Tool'.padEnd(30)} ${'Duration'.padEnd(15)} Status`);
  console.log(`${'-'.repeat(70)}`);

  results.forEach(r => {
    const statusIcon = r.status === 'success' ? '✅' : '❌';
    console.log(`${r.tool.padEnd(30)} ${(r.duration + 's').padEnd(15)} ${statusIcon}`);
  });

  console.log(`${'='.repeat(70)}\n`);

  // Group by MCP server
  const byServer = {
    filesystem: results.filter(r => ['list_allowed_directories', 'list_directory', 'read_text_file', 'get_file_info', 'directory_tree', 'search_files'].includes(r.tool)),
    tavily: results.filter(r => r.tool.startsWith('tavily-')),
    context7: results.filter(r => ['resolve-library-id', 'get-library-docs'].includes(r.tool))
  };

  console.log('Performance by MCP Server:');
  console.log(`${'='.repeat(70)}`);

  for (const [server, serverResults] of Object.entries(byServer)) {
    const avgDuration = serverResults.reduce((sum, r) => sum + r.duration, 0) / serverResults.length;
    const successRate = (serverResults.filter(r => r.status === 'success').length / serverResults.length * 100).toFixed(0);
    console.log(`${server.padEnd(15)} Avg: ${avgDuration.toFixed(2)}s | Success: ${successRate}%`);
  }

  console.log(`${'='.repeat(70)}\n`);
}

main().catch(console.error);