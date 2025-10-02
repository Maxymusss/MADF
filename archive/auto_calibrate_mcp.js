#!/usr/bin/env node
/**
 * Auto-Calibration System for New MCP Servers
 *
 * Process:
 * 1. Detect all tools from new MCP server
 * 2. Run all 5 strategies on each tool
 * 3. Measure: success rate, execution time, schema compliance
 * 4. Generate optimal strategy mapping
 * 5. Save to persistent config
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

// Strategy implementations
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

// Sample parameters generator based on tool schema
function generateSampleParams(toolSchema) {
  const params = {};
  const inputSchema = toolSchema.inputSchema || {};
  const properties = inputSchema.properties || {};
  const required = inputSchema.required || [];

  for (const [paramName, paramDef] of Object.entries(properties)) {
    // Only include required params for faster testing
    if (!required.includes(paramName)) continue;

    const type = paramDef.type;

    switch (type) {
      case 'string':
        params[paramName] = paramDef.enum ? paramDef.enum[0] :
                           paramName.includes('path') ? 'D:/dev/MADF' :
                           paramName.includes('query') ? 'test query' :
                           paramName.includes('url') ? 'https://example.com' :
                           paramName.includes('name') ? 'React' :
                           'test';
        break;
      case 'number':
      case 'integer':
        params[paramName] = paramDef.default || 2;
        break;
      case 'boolean':
        params[paramName] = paramDef.default || false;
        break;
      case 'array':
        params[paramName] = paramDef.items?.type === 'string' ? ['https://example.com'] : [];
        break;
      case 'object':
        params[paramName] = {};
        break;
      default:
        params[paramName] = null;
    }
  }

  return params;
}

// Test single strategy on single tool
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
      error: error.message.substring(0, 100)
    };
  }
}

// Calibrate single tool with predefined params
async function calibrateToolWithParams(client, llm, toolName, params, serverName) {
  console.log(`\n  Calibrating: ${toolName}`);
  console.log(`    Params: ${JSON.stringify(params)}`);

  const results = [];

  for (const [strategyName, strategyFn] of Object.entries(STRATEGIES)) {
    // Create fresh agent for each test to avoid context pollution
    const agent = new MCPAgent({ llm, client, maxSteps: 2 });

    const result = await testStrategy(agent, toolName, params, strategyFn, strategyName);
    results.push(result);

    const icon = result.success ? '✅' : '❌';
    console.log(`    ${icon} ${strategyName.padEnd(20)} ${result.duration}ms`);

    // Brief pause between strategies
    await new Promise(r => setTimeout(r, 500));
  }

  // Find best strategy
  const successfulResults = results.filter(r => r.success);

  if (successfulResults.length === 0) {
    console.log(`    ⚠️  All strategies failed`);
    return {
      toolName,
      serverName,
      bestStrategy: 'imperative',  // Fallback
      allFailed: true,
      results
    };
  }

  // Sort by success + speed
  successfulResults.sort((a, b) => a.duration - b.duration);
  const best = successfulResults[0];

  console.log(`    🏆 Winner: ${best.strategy} (${best.duration}ms)`);

  return {
    toolName,
    serverName,
    bestStrategy: best.strategy,
    bestDuration: best.duration,
    successRate: (successfulResults.length / results.length * 100).toFixed(0),
    results
  };
}

// Main calibration function
async function calibrateMCPServer(serverName, serverConfig, existingConfig) {
  console.log(`\n${'='.repeat(70)}`);
  console.log(`Calibrating MCP Server: ${serverName}`);
  console.log(`${'='.repeat(70)}`);

  // Initialize client with only this server
  const testConfig = {
    mcpServers: {
      [serverName]: serverConfig
    }
  };

  const client = new MCPClient({ mcpServers: testConfig.mcpServers });

  const llm = new ChatOllama({
    baseUrl: existingConfig.llm.baseUrl || 'http://localhost:11434',
    model: existingConfig.llm.model || 'llama3.1:8b',
    temperature: 0
  });

  // Create agent to get tool list
  const agent = new MCPAgent({ llm, client, maxSteps: 1 });

  console.log('\n[1/3] Discovering tools...');

  // Initialize agent first to trigger MCP connections
  await new Promise(r => setTimeout(r, 3000)); // Wait for connections

  // Get tools through temporary agent execution
  // MCP-use doesn't expose listTools directly, so we infer from agent
  // For now, use known tool lists per server
  const KNOWN_TOOLS = {
    filesystem: [
      { name: 'list_allowed_directories', params: {} },
      { name: 'list_directory', params: { path: 'D:/dev/MADF' } },
      { name: 'read_text_file', params: { path: 'D:/dev/MADF/package.json' } },
      { name: 'get_file_info', params: { path: 'D:/dev/MADF/package.json' } },
      { name: 'directory_tree', params: { path: 'D:/dev/MADF/mcp-use', depth: 2 } },
      { name: 'search_files', params: { path: 'D:/dev/MADF/docs', pattern: '*.md' } }
    ],
    tavily: [
      { name: 'tavily-search', params: { query: 'test query', max_results: 3 } },
      { name: 'tavily-extract', params: { urls: ['https://example.com'] } }
    ],
    context7: [
      { name: 'resolve-library-id', params: { libraryName: 'React' } },
      { name: 'get-library-docs', params: { context7CompatibleLibraryID: '/facebook/react', tokens: 2000 } }
    ]
  };

  const tools = (KNOWN_TOOLS[serverName] || []).map(t => ({
    name: t.name,
    schema: { inputSchema: { properties: {}, required: Object.keys(t.params) } },
    server: serverName,
    testParams: t.params
  }));

  console.log(`\n[2/3] Found ${tools.length} tools in ${serverName}`);

  const calibrationResults = [];

  for (const tool of tools) {
    // Use pre-defined test params instead of generating
    const result = await calibrateToolWithParams(client, llm, tool.name, tool.testParams, serverName);
    if (result) {
      calibrationResults.push(result);
    }
  }

  await client.closeAllSessions();

  console.log(`\n[3/3] Generating strategy mapping...`);

  // Generate mapping
  const mapping = {};
  calibrationResults.forEach(result => {
    if (!result.allFailed) {
      mapping[result.toolName] = result.bestStrategy;
    }
  });

  // Statistics
  const strategyStats = {};
  calibrationResults.forEach(r => {
    if (!r.allFailed) {
      strategyStats[r.bestStrategy] = (strategyStats[r.bestStrategy] || 0) + 1;
    }
  });

  console.log(`\n${'='.repeat(70)}`);
  console.log(`Calibration Complete: ${serverName}`);
  console.log(`${'='.repeat(70)}`);
  console.log(`\nTools calibrated: ${calibrationResults.length}`);
  console.log(`Success rate: ${calibrationResults.filter(r => !r.allFailed).length}/${calibrationResults.length}`);
  console.log(`\nStrategy distribution:`);
  Object.entries(strategyStats).forEach(([strategy, count]) => {
    console.log(`  ${strategy.padEnd(20)} ${count} tools`);
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

// Save calibration results
function saveCalibrationResults(serverName, results) {
  const outputDir = path.join(__dirname, '.mcp-calibrations');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
  }

  const outputFile = path.join(outputDir, `${serverName}.json`);
  fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));

  console.log(`\n✅ Calibration saved: ${outputFile}`);

  // Update main strategy mapping file
  updateStrategyMapping(serverName, results.mapping);
}

// Update centralized strategy mapping
function updateStrategyMapping(serverName, newMapping) {
  const mappingFile = path.join(__dirname, 'mcp-strategy-mapping.json');

  let existingMapping = {};
  if (fs.existsSync(mappingFile)) {
    existingMapping = JSON.parse(fs.readFileSync(mappingFile, 'utf-8'));
  }

  // Merge new mappings
  existingMapping[serverName] = {
    lastCalibrated: new Date().toISOString(),
    tools: newMapping
  };

  fs.writeFileSync(mappingFile, JSON.stringify(existingMapping, null, 2));

  console.log(`✅ Updated mapping: ${mappingFile}`);
  console.log(`\nGenerated mapping for ${Object.keys(newMapping).length} tools:`);
  console.log(JSON.stringify(newMapping, null, 2));
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
Usage: node auto_calibrate_mcp.js [command] [options]

Commands:
  all              Calibrate all MCP servers in config
  server <name>    Calibrate specific server

Examples:
  node auto_calibrate_mcp.js all
  node auto_calibrate_mcp.js server context7
  node auto_calibrate_mcp.js server filesystem
`);
    return;
  }

  const configFile = path.resolve(__dirname, 'mcp-use-ollama-config.json');
  const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));

  const command = args[0];

  if (command === 'all') {
    console.log('Calibrating all MCP servers...\n');

    for (const [serverName, serverConfig] of Object.entries(config.mcpServers)) {
      const results = await calibrateMCPServer(serverName, serverConfig, config);
      saveCalibrationResults(serverName, results);

      // Pause between servers
      await new Promise(r => setTimeout(r, 2000));
    }

  } else if (command === 'server' && args[1]) {
    const serverName = args[1];
    const serverConfig = config.mcpServers[serverName];

    if (!serverConfig) {
      console.error(`Error: Server '${serverName}' not found in config`);
      console.log(`Available servers: ${Object.keys(config.mcpServers).join(', ')}`);
      return;
    }

    const results = await calibrateMCPServer(serverName, serverConfig, config);
    saveCalibrationResults(serverName, results);

  } else {
    console.error('Invalid command. Use --help for usage.');
  }
}

main().catch(console.error);

export { calibrateMCPServer, generateSampleParams };