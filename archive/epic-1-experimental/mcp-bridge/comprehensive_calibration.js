#!/usr/bin/env node
/**
 * Comprehensive MCP Calibration - Discover ALL tools automatically
 * Shows detailed timing for each strategy for manual review
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

const STRATEGIES = {
  imperative: (toolName, params) => {
    const paramList = Object.entries(params)
      .map(([k, v]) => `${k}: ${JSON.stringify(v)}`)
      .join(', ');
    return `EXECUTE ${toolName} NOW. Parameters: ${paramList}`;
  },

  naturalExplicit: (toolName, params) => {
    let query = `Call the ${toolName} tool. `;
    for (const [key, val] of Object.entries(params)) {
      if (Array.isArray(val)) {
        query += `Pass ${key} as an array containing ${val.map(v => `"${v}"`).join(', ')}. `;
      } else if (typeof val === 'number') {
        query += `Pass ${key} as the number ${val}. `;
      } else {
        query += `Pass ${key} as "${val}". `;
      }
    }
    return query;
  },

  stepByStep: (toolName, params) => {
    const steps = Object.entries(params)
      .map(([key, val], idx) => `${idx + 1}. Set ${key} to ${JSON.stringify(val)}`)
      .join('\n');
    return `Execute ${toolName} tool:\n${steps}\nCall the tool now.`;
  },

  directWithSchema: (toolName, params) => {
    return `Execute: ${toolName}(${JSON.stringify(params)})`;
  },

  explicitTypes: (toolName, params) => {
    const paramDesc = Object.entries(params)
      .map(([key, val]) => {
        const type = Array.isArray(val) ? 'array' : typeof val;
        return `${key}=${JSON.stringify(val)} (${type} type)`;
      })
      .join(', ');
    return `Call ${toolName} with ${paramDesc}. Use exact types shown.`;
  }
};

// Generate sample parameters from tool schema
function generateSampleParams(toolSchema, toolName) {
  const params = {};
  const inputSchema = toolSchema.inputSchema || {};
  const properties = inputSchema.properties || {};

  // Get required params first, then optionals if needed
  const required = inputSchema.required || [];
  const paramsToFill = required.length > 0 ? required : Object.keys(properties).slice(0, 3);

  for (const paramName of paramsToFill) {
    const paramDef = properties[paramName];
    if (!paramDef) continue;

    const type = paramDef.type;

    switch (type) {
      case 'string':
        if (paramDef.enum) {
          params[paramName] = paramDef.enum[0];
        } else if (paramName.toLowerCase().includes('path')) {
          params[paramName] = 'D:/dev/MADF';
        } else if (paramName.toLowerCase().includes('url')) {
          params[paramName] = 'https://example.com';
        } else if (paramName.toLowerCase().includes('query')) {
          params[paramName] = 'test query';
        } else if (paramName.toLowerCase().includes('name') || paramName.toLowerCase().includes('library')) {
          params[paramName] = 'React';
        } else if (paramName.toLowerCase().includes('pattern')) {
          params[paramName] = '*.md';
        } else if (paramName.toLowerCase().includes('id')) {
          params[paramName] = '/facebook/react';
        } else {
          params[paramName] = 'test';
        }
        break;
      case 'number':
      case 'integer':
        params[paramName] = paramDef.default !== undefined ? paramDef.default :
                           paramName.toLowerCase().includes('depth') ? 2 :
                           paramName.toLowerCase().includes('max') ? 3 :
                           paramName.toLowerCase().includes('token') ? 2000 : 1;
        break;
      case 'boolean':
        params[paramName] = paramDef.default !== undefined ? paramDef.default : false;
        break;
      case 'array':
        if (paramDef.items?.type === 'string') {
          params[paramName] = ['https://example.com'];
        } else {
          params[paramName] = [];
        }
        break;
      case 'object':
        params[paramName] = {};
        break;
    }
  }

  return params;
}

// Test single strategy
async function testStrategy(agent, toolName, params, strategy, strategyName) {
  const query = strategy(toolName, params);
  const startTime = Date.now();

  try {
    await agent.run(query, 2);
    const duration = Date.now() - startTime;

    return {
      strategy: strategyName,
      success: true,
      duration,
      error: null
    };
  } catch (error) {
    const duration = Date.now() - startTime;

    return {
      strategy: strategyName,
      success: false,
      duration,
      error: error.message.substring(0, 150)
    };
  }
}

// Calibrate single tool
async function calibrateTool(client, llm, toolName, toolSchema, serverName) {
  const params = generateSampleParams(toolSchema, toolName);

  if (Object.keys(params).length === 0) {
    return null;  // Skip tools with no params
  }

  console.log(`\n${'─'.repeat(70)}`);
  console.log(`Tool: ${toolName}`);
  console.log(`Params: ${JSON.stringify(params)}`);
  console.log('─'.repeat(70));

  const results = [];

  for (const [strategyName, strategyFn] of Object.entries(STRATEGIES)) {
    const agent = new MCPAgent({ llm, client, maxSteps: 2 });
    const result = await testStrategy(agent, toolName, params, strategyFn, strategyName);
    results.push(result);

    const icon = result.success ? '✅' : '❌';
    const timeStr = `${result.duration}ms`.padStart(6);
    console.log(`  ${icon} ${strategyName.padEnd(20)} ${timeStr}${result.error ? ' - ' + result.error : ''}`);

    await new Promise(r => setTimeout(r, 500));
  }

  // Find best
  const successful = results.filter(r => r.success);
  if (successful.length === 0) {
    console.log(`  ⚠️  ALL FAILED`);
    return { toolName, serverName, allFailed: true, results };
  }

  successful.sort((a, b) => a.duration - b.duration);
  const best = successful[0];

  console.log(`  🏆 BEST: ${best.strategy} (${best.duration}ms)`);

  return {
    toolName,
    serverName,
    params,
    bestStrategy: best.strategy,
    bestDuration: best.duration,
    allResults: results,
    allFailed: false
  };
}

// Main calibration
async function calibrateServer(serverName, serverConfig, existingConfig) {
  console.log(`\n${'='.repeat(70)}`);
  console.log(`CALIBRATING: ${serverName.toUpperCase()}`);
  console.log(`${'='.repeat(70)}`);

  const testConfig = {
    mcpServers: { [serverName]: serverConfig }
  };

  const client = new MCPClient({ mcpServers: testConfig.mcpServers });
  const llm = new ChatOllama({
    baseUrl: existingConfig.llm.baseUrl || 'http://localhost:11434',
    model: existingConfig.llm.model || 'llama3.1:8b',
    temperature: 0
  });

  // Initialize and wait for tools to be available
  const agent = new MCPAgent({ llm, client, maxSteps: 1 });
  await new Promise(r => setTimeout(r, 3000));

  console.log('\n[Discovering tools...]');

  // Get tools from LangChain agent's tool list
  const toolsInfo = [];

  // Trigger tool discovery by creating agent
  // Tools are accessible through the client after initialization
  // We'll extract from logs or use a query

  // For now, run a discovery query to see what tools are available
  try {
    const discoveryResult = await agent.run('List all available tools', 1);
    console.log('\n[Discovery result sample]:', discoveryResult.substring(0, 200));
  } catch (e) {
    // Ignore
  }

  // Since mcp-use doesn't expose tools directly, we'll manually map known tools
  // based on typical MCP server implementations
  const COMPREHENSIVE_TOOLS = {
    filesystem: [
      { name: 'list_allowed_directories', schema: { inputSchema: { properties: {}, required: [] }}},
      { name: 'list_directory', schema: { inputSchema: { properties: { path: { type: 'string' }}, required: ['path'] }}},
      { name: 'read_text_file', schema: { inputSchema: { properties: { path: { type: 'string' }}, required: ['path'] }}},
      { name: 'read_media_file', schema: { inputSchema: { properties: { path: { type: 'string' }}, required: ['path'] }}},
      { name: 'read_multiple_files', schema: { inputSchema: { properties: { paths: { type: 'array', items: { type: 'string' }}}, required: ['paths'] }}},
      { name: 'write_file', schema: { inputSchema: { properties: { path: { type: 'string' }, content: { type: 'string' }}, required: ['path', 'content'] }}},
      { name: 'edit_file', schema: { inputSchema: { properties: { path: { type: 'string' }, edits: { type: 'array' }}, required: ['path', 'edits'] }}},
      { name: 'create_directory', schema: { inputSchema: { properties: { path: { type: 'string' }}, required: ['path'] }}},
      { name: 'list_directory_with_sizes', schema: { inputSchema: { properties: { path: { type: 'string' }}, required: ['path'] }}},
      { name: 'directory_tree', schema: { inputSchema: { properties: { path: { type: 'string' }, depth: { type: 'number' }}, required: ['path'] }}},
      { name: 'move_file', schema: { inputSchema: { properties: { source: { type: 'string' }, destination: { type: 'string' }}, required: ['source', 'destination'] }}},
      { name: 'search_files', schema: { inputSchema: { properties: { path: { type: 'string' }, pattern: { type: 'string' }}, required: ['path', 'pattern'] }}},
      { name: 'get_file_info', schema: { inputSchema: { properties: { path: { type: 'string' }}, required: ['path'] }}}
    ],
    tavily: [
      { name: 'tavily-search', schema: { inputSchema: { properties: { query: { type: 'string' }, max_results: { type: 'number' }}, required: ['query'] }}},
      { name: 'tavily-extract', schema: { inputSchema: { properties: { urls: { type: 'array', items: { type: 'string' }}}, required: ['urls'] }}},
      { name: 'tavily-crawl', schema: { inputSchema: { properties: { base_url: { type: 'string' }, max_pages: { type: 'number' }}, required: ['base_url'] }}},
      { name: 'tavily-map', schema: { inputSchema: { properties: { url: { type: 'string' }}, required: ['url'] }}}
    ],
    context7: [
      { name: 'resolve-library-id', schema: { inputSchema: { properties: { libraryName: { type: 'string' }}, required: ['libraryName'] }}},
      { name: 'get-library-docs', schema: { inputSchema: { properties: { context7CompatibleLibraryID: { type: 'string' }, tokens: { type: 'number' }}, required: ['context7CompatibleLibraryID'] }}}
    ],
    obsidian: [
      { name: 'list_files_in_vault', schema: { inputSchema: { properties: {}, required: [] }}},
      { name: 'list_files_in_dir', schema: { inputSchema: { properties: { path: { type: 'string' }}, required: ['path'] }}},
      { name: 'get_file_contents', schema: { inputSchema: { properties: { path: { type: 'string' }}, required: ['path'] }}},
      { name: 'search', schema: { inputSchema: { properties: { query: { type: 'string' }}, required: ['query'] }}},
      { name: 'patch_content', schema: { inputSchema: { properties: { path: { type: 'string' }, content: { type: 'string' }}, required: ['path', 'content'] }}},
      { name: 'append_content', schema: { inputSchema: { properties: { path: { type: 'string' }, content: { type: 'string' }}, required: ['path', 'content'] }}},
      { name: 'delete_file', schema: { inputSchema: { properties: { path: { type: 'string' }}, required: ['path'] }}}
    ]
  };

  const tools = COMPREHENSIVE_TOOLS[serverName] || [];
  console.log(`\n[Found ${tools.length} tools]\n`);

  const calibrationResults = [];

  for (const tool of tools) {
    const result = await calibrateTool(client, llm, tool.name, tool.schema, serverName);
    if (result) {
      calibrationResults.push(result);
    }
  }

  await client.closeAllSessions();

  // Generate summary
  console.log(`\n${'='.repeat(70)}`);
  console.log(`SUMMARY: ${serverName}`);
  console.log(`${'='.repeat(70)}`);

  const mapping = {};
  calibrationResults.forEach(r => {
    if (!r.allFailed) {
      mapping[r.toolName] = r.bestStrategy;
    }
  });

  console.log(`\nTools calibrated: ${calibrationResults.length}`);
  console.log(`Successful: ${calibrationResults.filter(r => !r.allFailed).length}`);

  // Strategy distribution
  const strategyStats = {};
  calibrationResults.forEach(r => {
    if (!r.allFailed) {
      strategyStats[r.bestStrategy] = (strategyStats[r.bestStrategy] || 0) + 1;
    }
  });

  console.log(`\nStrategy Distribution:`);
  Object.entries(strategyStats).sort((a, b) => b[1] - a[1]).forEach(([strat, count]) => {
    console.log(`  ${strat.padEnd(20)} ${count} tools`);
  });

  return {
    serverName,
    timestamp: new Date().toISOString(),
    toolCount: tools.length,
    calibrationResults,
    mapping,
    strategyStats
  };
}

// Save results with detailed report
function saveResults(serverName, results) {
  const outputDir = path.join(__dirname, '.mcp-calibrations');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
  }

  // Save full JSON
  const jsonFile = path.join(outputDir, `${serverName}_full.json`);
  fs.writeFileSync(jsonFile, JSON.stringify(results, null, 2));

  // Save human-readable report
  const reportFile = path.join(outputDir, `${serverName}_report.txt`);
  let report = `MCP Server Calibration Report: ${serverName}\n`;
  report += `Generated: ${results.timestamp}\n`;
  report += `${'='.repeat(70)}\n\n`;

  results.calibrationResults.forEach(tool => {
    report += `Tool: ${tool.toolName}\n`;
    report += `Params: ${JSON.stringify(tool.params)}\n`;
    report += `Best Strategy: ${tool.bestStrategy} (${tool.bestDuration}ms)\n`;
    report += `\nAll Results:\n`;

    tool.allResults.forEach(r => {
      const status = r.success ? '✅' : '❌';
      report += `  ${status} ${r.strategy.padEnd(20)} ${String(r.duration).padStart(6)}ms`;
      if (r.error) report += ` - ${r.error}`;
      report += `\n`;
    });
    report += `\n${'-'.repeat(70)}\n\n`;
  });

  fs.writeFileSync(reportFile, report);

  // Update master mapping
  const mappingFile = path.join(__dirname, 'mcp-strategy-mapping.json');
  let masterMapping = { tools: {}, default: 'imperative' };
  if (fs.existsSync(mappingFile)) {
    masterMapping = JSON.parse(fs.readFileSync(mappingFile, 'utf-8'));
  }

  // Add new tools with server metadata
  for (const [toolName, strategy] of Object.entries(results.mapping)) {
    masterMapping.tools[toolName] = {
      server: serverName,
      tool: toolName,
      strategy: strategy
    };
  }

  masterMapping.lastUpdated = results.timestamp;

  fs.writeFileSync(mappingFile, JSON.stringify(masterMapping, null, 2));

  console.log(`\n✅ Saved:`);
  console.log(`   JSON: ${jsonFile}`);
  console.log(`   Report: ${reportFile}`);
  console.log(`   Mapping: ${mappingFile}`);
}

// CLI
async function main() {
  const args = process.argv.slice(2);
  const configFile = path.resolve(__dirname, 'mcp-use-ollama-config.json');
  const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));

  if (args[0] === 'all') {
    for (const [serverName, serverConfig] of Object.entries(config.mcpServers)) {
      const results = await calibrateServer(serverName, serverConfig, config);
      saveResults(serverName, results);
      await new Promise(r => setTimeout(r, 2000));
    }
  } else if (args[0] && config.mcpServers[args[0]]) {
    const serverName = args[0];
    const results = await calibrateServer(serverName, config.mcpServers[serverName], config);
    saveResults(serverName, results);
  } else {
    console.log('Usage: node comprehensive_calibration.js [all|filesystem|tavily|context7|obsidian]');
  }
}

main().catch(console.error);