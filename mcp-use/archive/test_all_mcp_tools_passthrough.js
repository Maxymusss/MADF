#!/usr/bin/env node
/**
 * Test all MCP tools with PassThroughLLM (structured input)
 * Uses qwen3-coder:480b-cloud with direct tool execution
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

// No wrapper needed - rules embedded in qwen3-coder-mcp modelfile

const configFile = path.resolve(__dirname, 'mcp-use-ollama-config.json');
const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));

// Structured test cases: ["server", "tool", {...params}]
const TEST_CASES = [
  // Filesystem MCP
  {
    name: 'list_allowed_directories',
    input: ["filesystem", "list_allowed_directories", {}]
  },
  {
    name: 'list_directory',
    input: ["filesystem", "list_directory", {"path": "D:/dev/MADF"}]
  },
  {
    name: 'read_text_file',
    input: ["filesystem", "read_text_file", {"path": "D:/dev/MADF/package.json"}]
  },
  {
    name: 'get_file_info',
    input: ["filesystem", "get_file_info", {"path": "D:/dev/MADF/package.json"}]
  },
  {
    name: 'directory_tree',
    input: ["filesystem", "directory_tree", {"path": "D:/dev/MADF/mcp-use", "depth": 2}]
  },
  {
    name: 'search_files',
    input: ["filesystem", "search_files", {"path": "D:/dev/MADF/docs", "pattern": "*.md"}]
  },

  // Tavily MCP
  {
    name: 'tavily-search',
    input: ["tavily", "tavily-search", {"query": "LangChain agents tutorial", "max_results": 3}]
  },
  {
    name: 'tavily-extract',
    input: ["tavily", "tavily-extract", {"urls": ["https://example.com"]}]
  },

  // Context7 MCP
  {
    name: 'resolve-library-id',
    input: ["context7", "resolve-library-id", {"libraryName": "Next.js"}]
  },
  {
    name: 'get-library-docs',
    input: ["context7", "get-library-docs", {"context7CompatibleLibraryID": "/vercel/next.js", "tokens": 2000}]
  }
];

async function testTool(testCase, agent) {
  console.log(`\n[${'='.repeat(60)}]`);
  console.log(`Testing: ${testCase.name}`);
  console.log(`Input: ${JSON.stringify(testCase.input)}`);
  console.log(`[${'='.repeat(60)}]`);

  const startTime = Date.now();

  try {
    // Convert structured input to explicit tool call instruction
    const [server, toolName, params] = testCase.input;
    const paramsStr = Object.keys(params).length > 0
      ? ` with parameters ${JSON.stringify(params)}`
      : '';
    const query = `Call the ${toolName} tool${paramsStr}`;
    const result = await agent.run(query, 3);
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
  console.log('MCP Tool Performance Test - PassThrough (Structured Input)');
  console.log(`${'='.repeat(70)}`);
  console.log(`Config: ${configFile}`);
  console.log(`Model: ${config.llm.model}`);
  console.log(`Mode: Structured input with PassThroughLLM`);
  console.log(`Total tests: ${TEST_CASES.length}`);
  console.log(`${'='.repeat(70)}\n`);

  const client = new MCPClient({ mcpServers: config.mcpServers });

  const llm = new ChatOllama({
    baseUrl: config.llm.baseUrl || 'http://localhost:11434',
    model: config.llm.model || 'qwen3-coder-mcp',
    temperature: 0
  });

  const agent = new MCPAgent({ llm, client, maxSteps: 3 });

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
    if (serverResults.length === 0) continue;
    const avgDuration = serverResults.reduce((sum, r) => sum + r.duration, 0) / serverResults.length;
    const successRate = (serverResults.filter(r => r.status === 'success').length / serverResults.length * 100).toFixed(0);
    console.log(`${server.padEnd(15)} Avg: ${avgDuration.toFixed(2)}s | Success: ${successRate}%`);
  }

  console.log(`${'='.repeat(70)}\n`);

  // Compare to natural language mode
  console.log('Comparison to Natural Language Mode:');
  console.log(`${'='.repeat(70)}`);
  console.log('Natural Language Mode:');
  console.log('  - Filesystem: 9.54s avg (100% success)');
  console.log('  - Tavily: 4.64s avg (100% success, but wrong tools called)');
  console.log('  - Context7: 10.84s avg (100% success)');
  console.log('');
  console.log('Structured Input Mode (this test):');

  for (const [server, serverResults] of Object.entries(byServer)) {
    if (serverResults.length === 0) continue;
    const avgDuration = serverResults.reduce((sum, r) => sum + r.duration, 0) / serverResults.length;
    const successRate = (serverResults.filter(r => r.status === 'success').length / serverResults.length * 100).toFixed(0);
    console.log(`  - ${server}: ${avgDuration.toFixed(2)}s avg (${successRate}% success)`);
  }

  console.log(`${'='.repeat(70)}\n`);
}

main().catch(console.error);