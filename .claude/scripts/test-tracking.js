#!/usr/bin/env node

/**
 * Test Tool Tracking System
 * Generates sample tracking data and tests all functionality
 */

import { trackTool } from '../tools/tool-tracker.js';
import ToolAnalytics from '../tools/tool-analytics.js';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function testTrackingSystem() {
  console.log('🧪 Testing Tool Tracking System...');
  console.log('─'.repeat(40));

  // Test 1: Basic tracking
  console.log('1. Testing basic tool tracking...');

  trackTool({
    toolName: 'test_tool',
    serverName: 'test_server',
    toolType: 'mcp',
    parameters: { param1: 'value1', param2: 'value2' },
    executionTime: 150,
    success: true,
    result: { status: 'ok', data: 'test result' }
  });

  trackTool({
    toolName: 'read_file',
    toolType: 'native',
    parameters: { file_path: '/test/path.txt' },
    executionTime: 75,
    success: true,
    result: { content: 'file content...' }
  });

  trackTool({
    toolName: 'failing_tool',
    serverName: 'unreliable_server',
    toolType: 'mcp',
    parameters: { action: 'test' },
    executionTime: 200,
    success: false,
    error: 'Connection timeout'
  });

  // Test 2: Multiple calls of same tool
  console.log('2. Testing multiple calls...');
  for (let i = 0; i < 5; i++) {
    trackTool({
      toolName: 'frequent_tool',
      serverName: 'github',
      toolType: 'mcp',
      parameters: { query: `test${i}` },
      executionTime: Math.random() * 100 + 50,
      success: Math.random() > 0.2,
      result: { results: i + 1 }
    });
    await sleep(10); // Small delay to vary timestamps
  }

  // Test 3: Different tool types
  console.log('3. Testing different tool types...');

  const toolTypes = ['mcp', 'agent', 'native', 'command', 'hook'];
  for (const type of toolTypes) {
    trackTool({
      toolName: `${type}_example`,
      toolType: type,
      parameters: { type: type },
      executionTime: Math.random() * 300 + 100,
      success: Math.random() > 0.1,
      result: { type: type }
    });
  }

  // Test 4: Analytics
  console.log('4. Testing analytics generation...');

  const analytics = new ToolAnalytics();
  const report = analytics.generateReport({
    timeframe: 'session',
    detailed: true,
    format: 'text'
  });

  console.log('\n📊 Generated Report:');
  console.log(report);

  // Test 5: Insights
  console.log('\n🧠 Testing insights...');
  const insights = analytics.getInsights();
  console.log(insights);

  // Test 6: Export functionality
  console.log('\n📤 Testing export...');
  try {
    const data = analytics.loadData();
    if (data) {
      console.log(`✅ Data loaded: ${data.totalCalls} total calls`);
      console.log(`✅ Sessions: ${Object.keys(data.sessions).length}`);
    }
  } catch (error) {
    console.log(`❌ Export test failed: ${error.message}`);
  }

  console.log('\n✅ All tests completed!');
  console.log('\nTo view detailed reports, run:');
  console.log('  node .claude/scripts/tool-stats.js report --detailed');
  console.log('  node .claude/scripts/tool-stats.js insights');
  console.log('  node .claude/scripts/tool-stats.js export --format csv');
}

// Run tests
testTrackingSystem().catch(console.error);