#!/usr/bin/env node
/**
 * Test different fix strategies for failed MCP tools
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

// Fix Strategy 1: Explicit Type Instruction
const FIX_STRATEGIES = {
  explicitTypes: (toolName, params) => {
    const paramDesc = Object.entries(params)
      .map(([key, val]) => {
        const type = Array.isArray(val) ? 'array' : typeof val;
        return `${key}=${JSON.stringify(val)} (${type} type)`;
      })
      .join(', ');
    return `Call ${toolName} with ${paramDesc}. Use exact types shown.`;
  },

  // Fix Strategy 2: Step-by-Step Parameter Construction
  stepByStep: (toolName, params) => {
    const steps = Object.entries(params)
      .map(([key, val], idx) => `${idx + 1}. Set ${key} to ${JSON.stringify(val)}`)
      .join('\n');
    return `Execute ${toolName} tool:\n${steps}\nCall the tool now.`;
  },

  // Fix Strategy 3: Direct Command with Schema
  directWithSchema: (toolName, params) => {
    return `Execute: ${toolName}(${JSON.stringify(params)})`;
  },

  // Fix Strategy 4: Imperative Instruction
  imperative: (toolName, params) => {
    const paramList = Object.entries(params)
      .map(([k, v]) => `${k}: ${JSON.stringify(v)}`)
      .join(', ');
    return `EXECUTE ${toolName} NOW. Parameters: ${paramList}`;
  },

  // Fix Strategy 5: Natural Language with Explicit Format
  naturalExplicit: (toolName, params) => {
    let desc = `Call the ${toolName} tool. `;
    for (const [key, val] of Object.entries(params)) {
      if (Array.isArray(val)) {
        desc += `Pass ${key} as an array containing ${val.map(v => `"${v}"`).join(', ')}. `;
      } else if (typeof val === 'number') {
        desc += `Pass ${key} as the number ${val}. `;
      } else {
        desc += `Pass ${key} as "${val}". `;
      }
    }
    return desc;
  }
};

const FAILED_TOOLS = [
  {
    name: 'directory_tree',
    input: ["filesystem", "directory_tree", {"path": "D:/dev/MADF/mcp-use", "depth": 2}],
    issue: 'Type conversion: depth number → string',
    strategies: ['explicitTypes', 'naturalExplicit', 'directWithSchema']
  },
  {
    name: 'search_files',
    input: ["filesystem", "search_files", {"path": "D:/dev/MADF/docs", "pattern": "*.md"}],
    issue: 'Context bleeding from previous test',
    strategies: ['imperative', 'stepByStep', 'naturalExplicit']
  },
  {
    name: 'tavily-search',
    input: ["tavily", "tavily-search", {"query": "LangChain agents tutorial", "max_results": 3}],
    issue: 'Context bleeding + type conversion',
    strategies: ['explicitTypes', 'imperative', 'directWithSchema']
  },
  {
    name: 'tavily-extract',
    input: ["tavily", "tavily-extract", {"urls": ["https://example.com"]}],
    issue: 'Array serialization: array → string',
    strategies: ['naturalExplicit', 'stepByStep', 'explicitTypes']
  },
  {
    name: 'resolve-library-id',
    input: ["context7", "resolve-library-id", {"libraryName": "Next.js"}],
    issue: 'No tool call, returns JSON text',
    strategies: ['imperative', 'directWithSchema', 'naturalExplicit']
  }
];

async function testStrategy(testCase, strategy, agent) {
  const [server, toolName, params] = testCase.input;
  const query = FIX_STRATEGIES[strategy](toolName, params);

  console.log(`\n  Strategy: ${strategy}`);
  console.log(`  Query: ${query.substring(0, 100)}...`);

  const startTime = Date.now();

  try {
    const result = await agent.run(query, 2);
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);

    // Check if correct tool was called
    const logs = [];
    const originalLog = console.log;
    console.log = (...args) => logs.push(args.join(' '));

    console.log = originalLog;

    return {
      strategy,
      duration: parseFloat(duration),
      success: true,
      result: result.substring(0, 200)
    };
  } catch (error) {
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    return {
      strategy,
      duration: parseFloat(duration),
      success: false,
      error: error.message.substring(0, 100)
    };
  }
}

async function main() {
  console.log(`${'='.repeat(70)}`);
  console.log('Testing Fix Strategies for Failed MCP Tools');
  console.log(`${'='.repeat(70)}\n`);

  const client = new MCPClient({ mcpServers: config.mcpServers });
  const llm = new ChatOllama({
    baseUrl: config.llm.baseUrl || 'http://localhost:11434',
    model: config.llm.model || 'llama3.1:8b',
    temperature: 0
  });

  const results = [];

  for (const testCase of FAILED_TOOLS) {
    console.log(`\n${'='.repeat(70)}`);
    console.log(`Testing: ${testCase.name}`);
    console.log(`Issue: ${testCase.issue}`);
    console.log(`${'='.repeat(70)}`);

    const testResults = [];

    for (const strategy of testCase.strategies) {
      // Create fresh agent for each test to avoid context bleeding
      const agent = new MCPAgent({ llm, client, maxSteps: 2 });
      const result = await testStrategy(testCase, strategy, agent);
      testResults.push(result);

      const statusIcon = result.success ? '✅' : '❌';
      console.log(`  ${statusIcon} ${result.duration}s - ${result.success ? 'SUCCESS' : result.error}`);

      // Brief pause between tests
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    results.push({
      tool: testCase.name,
      issue: testCase.issue,
      results: testResults,
      bestStrategy: testResults.sort((a, b) => {
        if (a.success && !b.success) return -1;
        if (!a.success && b.success) return 1;
        return a.duration - b.duration;
      })[0]
    });
  }

  await client.closeAllSessions();

  // Summary
  console.log(`\n\n${'='.repeat(70)}`);
  console.log('SUMMARY: Best Strategy per Tool');
  console.log(`${'='.repeat(70)}\n`);

  for (const result of results) {
    console.log(`${result.tool.padEnd(25)} → ${result.bestStrategy.strategy.padEnd(20)} (${result.bestStrategy.duration}s)`);
  }

  // Group by strategy effectiveness
  console.log(`\n${'='.repeat(70)}`);
  console.log('Strategy Effectiveness');
  console.log(`${'='.repeat(70)}\n`);

  const strategyStats = {};
  results.forEach(r => {
    r.results.forEach(res => {
      if (!strategyStats[res.strategy]) {
        strategyStats[res.strategy] = { successes: 0, total: 0, avgDuration: 0 };
      }
      strategyStats[res.strategy].total++;
      if (res.success) strategyStats[res.strategy].successes++;
      strategyStats[res.strategy].avgDuration += res.duration;
    });
  });

  Object.entries(strategyStats).forEach(([strategy, stats]) => {
    const successRate = ((stats.successes / stats.total) * 100).toFixed(0);
    const avgDur = (stats.avgDuration / stats.total).toFixed(2);
    console.log(`${strategy.padEnd(20)} Success: ${successRate}% | Avg: ${avgDur}s | Tests: ${stats.total}`);
  });

  console.log(`\n${'='.repeat(70)}\n`);
}

main().catch(console.error);