#!/usr/bin/env node

// Test script for universal proxy functionality
import { spawn } from 'child_process';

console.log('🧪 Testing Universal MCP Proxy');
console.log('===============================\n');

async function testProxy() {
  const env = {
    ...process.env,
    GITHUB_TOKEN: 'test_token',
    ENABLED_MCP_SERVERS: 'github'
  };

  const proxy = spawn('node', ['.claude/mcp-wrappers/universal-proxy.js'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    env
  });

  let output = '';

  proxy.stderr.on('data', (data) => {
    const message = data.toString();
    console.log('Proxy:', message.trim());
    output += message;
  });

  proxy.stdout.on('data', (data) => {
    console.log('Stdout:', data.toString().trim());
  });

  // Wait for initialization
  await new Promise((resolve) => {
    const checkInit = () => {
      if (output.includes('Universal proxy started') || output.includes('GitHub MCP Server running')) {
        resolve();
      } else {
        setTimeout(checkInit, 100);
      }
    };
    checkInit();
  });

  console.log('\n✅ Proxy started successfully!');

  // Send list_tools request
  const listToolsRequest = JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/list'
  }) + '\n';

  console.log('\n📝 Requesting tools list...');
  proxy.stdin.write(listToolsRequest);

  // Test enable server tool
  setTimeout(() => {
    const enableServerRequest = JSON.stringify({
      jsonrpc: '2.0',
      id: 2,
      method: 'tools/call',
      params: {
        name: 'mcp__unipxy__list_servers',
        arguments: {}
      }
    }) + '\n';

    console.log('\n🔧 Testing mcp__unipxy__list_servers...');
    proxy.stdin.write(enableServerRequest);
  }, 1000);

  // Wait for response
  await new Promise((resolve) => setTimeout(resolve, 2000));

  proxy.kill();
  console.log('\n🏁 Test completed');
}

testProxy().catch(console.error);