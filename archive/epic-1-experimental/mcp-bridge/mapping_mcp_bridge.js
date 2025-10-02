#!/usr/bin/env node
/**
 * Intelligent MCP Bridge - Auto-selects best query strategy per tool
 *
 * Integration Approaches:
 * 1. Tool-Based Selection: Map tools to proven strategies (calibrated)
 * 2. Parameter Analysis: Auto-detect types and choose strategy (fallback)
 * 3. Fallback Chain: Try strategies in order until success
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

// ============================================================================
// INTEGRATION APPROACH 1: Tool-Based Strategy Mapping (Calibrated)
// ============================================================================

// Load calibrated mappings from mcp-strategy-mapping.json
function loadCalibratedMappings() {
  const mappingFile = path.join(__dirname, 'mcp-strategy-mapping.json');
  try {
    const data = JSON.parse(fs.readFileSync(mappingFile, 'utf-8'));
    return data.tools || {};
  } catch (e) {
    console.warn('[Bridge] Could not load mcp-strategy-mapping.json, using defaults');
    return {};
  }
}

const TOOL_STRATEGY_MAP = loadCalibratedMappings();
const DEFAULT_STRATEGY = 'imperative';

// ============================================================================
// INTEGRATION APPROACH 2: Parameter Analysis (Smart Detection)
// ============================================================================
function analyzeParameters(params) {
  const analysis = {
    hasArrays: false,
    hasNumbers: false,
    hasComplex: false,
    paramCount: 0,
    types: {}
  };

  for (const [key, val] of Object.entries(params)) {
    analysis.paramCount++;

    if (Array.isArray(val)) {
      analysis.hasArrays = true;
      analysis.types[key] = 'array';
    } else if (typeof val === 'number') {
      analysis.hasNumbers = true;
      analysis.types[key] = 'number';
    } else if (typeof val === 'object' && val !== null) {
      analysis.hasComplex = true;
      analysis.types[key] = 'object';
    } else {
      analysis.types[key] = 'string';
    }
  }

  return analysis;
}

function selectStrategyByParams(params) {
  const analysis = analyzeParameters(params);

  // Rule 1: Arrays need explicit handling
  if (analysis.hasArrays) {
    return 'naturalExplicit';  // or 'stepByStep'
  }

  // Rule 2: Numbers need type preservation
  if (analysis.hasNumbers) {
    return 'naturalExplicit';
  }

  // Rule 3: Complex/many params benefit from step-by-step
  if (analysis.paramCount > 2 || analysis.hasComplex) {
    return 'stepByStep';
  }

  // Rule 4: Simple params use fast imperative
  return 'imperative';
}

// ============================================================================
// INTEGRATION APPROACH 3: Fallback Chain (Retry with Different Strategies)
// ============================================================================
const FALLBACK_CHAINS = {
  // Standard chain for most tools
  standard: ['imperative', 'naturalExplicit', 'stepByStep'],

  // Fast chain for simple tools (no arrays/numbers)
  fast: ['imperative', 'stepByStep'],

  // Type-safe chain for complex params
  typeSafe: ['naturalExplicit', 'stepByStep', 'imperative'],

  // Array-focused chain
  arrayFocused: ['stepByStep', 'naturalExplicit', 'imperative']
};

function selectFallbackChain(toolName, params) {
  const analysis = analyzeParameters(params);

  if (analysis.hasArrays) return FALLBACK_CHAINS.arrayFocused;
  if (analysis.hasNumbers) return FALLBACK_CHAINS.typeSafe;
  if (analysis.paramCount <= 1) return FALLBACK_CHAINS.fast;

  return FALLBACK_CHAINS.standard;
}

// ============================================================================
// Strategy Generators
// ============================================================================
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
  }
};

// ============================================================================
// Main Bridge Class - Simplified Interface
// ============================================================================
class IntelligentMCPBridge {
  constructor(config, integrationMode = 'hybrid') {
    this.config = config;
    this.integrationMode = integrationMode;
    this.client = null;
    this.agent = null;
  }

  async initialize() {
    this.client = new MCPClient({ mcpServers: this.config.mcpServers });

    const llm = new ChatOllama({
      baseUrl: this.config.llm.baseUrl || 'http://localhost:11434',
      model: this.config.llm.model || 'llama3.1:8b',
      temperature: 0
    });

    this.agent = new MCPAgent({ llm, client: this.client, maxSteps: 3 });
  }

  selectStrategy(toolName, params) {
    switch (this.integrationMode) {
      case 'toolBased':
        // Use calibrated mapping only
        const toolConfig = TOOL_STRATEGY_MAP[toolName];
        return toolConfig?.strategy || DEFAULT_STRATEGY;

      case 'paramBased':
        // Analyze parameters to choose strategy
        return selectStrategyByParams(params);

      case 'hybrid':
        // Combine approaches: calibrated mapping → parameter analysis fallback
        const mappedConfig = TOOL_STRATEGY_MAP[toolName];
        if (mappedConfig?.strategy) return mappedConfig.strategy;

        return selectStrategyByParams(params);

      default:
        return DEFAULT_STRATEGY;
    }
  }

  async executeTool(server, toolName, params, useFallback = true) {
    const strategy = this.selectStrategy(toolName, params);

    console.log(`[Bridge] Tool: ${toolName} | Strategy: ${strategy}`);

    const query = STRATEGIES[strategy](toolName, params);
    const startTime = Date.now();

    try {
      const result = await this.agent.run(query, 3);
      const duration = Date.now() - startTime;

      return {
        success: true,
        result,
        strategy,
        duration
      };
    } catch (error) {
      const duration = Date.now() - startTime;

      // Fallback chain if enabled
      if (useFallback) {
        console.log(`[Bridge] Strategy ${strategy} failed, trying fallback...`);
        return await this.executeWithFallback(server, toolName, params, strategy);
      }

      return {
        success: false,
        error: error.message,
        strategy,
        duration
      };
    }
  }

  async executeWithFallback(server, toolName, params, failedStrategy) {
    const chain = selectFallbackChain(toolName, params);
    const remainingStrategies = chain.filter(s => s !== failedStrategy);

    for (const strategy of remainingStrategies) {
      console.log(`[Bridge] Trying fallback strategy: ${strategy}`);

      const query = STRATEGIES[strategy](toolName, params);
      const startTime = Date.now();

      try {
        // Create fresh agent to avoid context pollution
        const llm = new ChatOllama({
          baseUrl: this.config.llm.baseUrl,
          model: this.config.llm.model,
          temperature: 0
        });
        const agent = new MCPAgent({ llm, client: this.client, maxSteps: 3 });

        const result = await agent.run(query, 3);
        const duration = Date.now() - startTime;

        return {
          success: true,
          result,
          strategy,
          duration,
          fallbackUsed: true
        };
      } catch (error) {
        continue;  // Try next strategy
      }
    }

    return {
      success: false,
      error: 'All fallback strategies failed',
      attemptedStrategies: [failedStrategy, ...remainingStrategies]
    };
  }

  async close() {
    if (this.client) {
      await this.client.closeAllSessions();
    }
  }
}

// ============================================================================
// Example Usage
// ============================================================================
async function demonstrateIntegrations() {
  const configFile = path.resolve(__dirname, 'mcp-use-ollama-config.json');
  const config = JSON.parse(fs.readFileSync(configFile, 'utf-8'));

  console.log('='.repeat(70));
  console.log('Intelligent MCP Bridge - Integration Modes Demo');
  console.log('='.repeat(70));

  const modes = ['toolBased', 'paramBased', 'hybrid'];

  const testCases = [
    ['filesystem', 'directory_tree', { path: 'D:/dev/MADF/mcp-use', depth: 2 }],
    ['tavily', 'tavily-extract', { urls: ['https://example.com'] }],
    ['context7', 'resolve-library-id', { libraryName: 'React' }]
  ];

  for (const mode of modes) {
    console.log(`\n${'='.repeat(70)}`);
    console.log(`Mode: ${mode.toUpperCase()}`);
    console.log('='.repeat(70));

    const bridge = new IntelligentMCPBridge(config, mode);
    await bridge.initialize();

    for (const [server, tool, params] of testCases) {
      const result = await bridge.executeTool(server, tool, params);
      console.log(`\n${tool}: ${result.success ? '[OK]' : '[FAIL]'} (${result.strategy}, ${result.duration}ms)`);
    }

    await bridge.close();
    await new Promise(r => setTimeout(r, 1000));
  }

  console.log('\n' + '='.repeat(70));
  console.log('Recommendation: Use HYBRID mode (calibrated mapping + param fallback)');
  console.log('='.repeat(70));
}

// Run demo if called directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  demonstrateIntegrations().catch(console.error);
}

export { IntelligentMCPBridge, STRATEGIES, TOOL_STRATEGY_MAP };