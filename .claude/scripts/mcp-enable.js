#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function enableMCP(serverName) {
  const proxyConfigPath = path.join(__dirname, '..', 'mcp-proxy-config.json');
  const optionalConfigPath = path.join(__dirname, '..', '..', '.mcp.optional.json');

  // Load proxy config
  let proxyConfig = { enabledServers: {} };
  if (fs.existsSync(proxyConfigPath)) {
    proxyConfig = JSON.parse(fs.readFileSync(proxyConfigPath, 'utf8'));
  }

  // Load server definition from optional config
  if (!fs.existsSync(optionalConfigPath)) {
    console.error('❌ .mcp.optional.json not found');
    process.exit(1);
  }

  const optionalConfig = JSON.parse(fs.readFileSync(optionalConfigPath, 'utf8'));
  const serverConfig = optionalConfig.mcpServers[serverName];

  if (!serverConfig) {
    console.error(`❌ Server '${serverName}' not found in .mcp.optional.json`);
    console.log('📋 Available servers:');
    Object.keys(optionalConfig.mcpServers).forEach(name => {
      console.log(`   - ${name}`);
    });
    process.exit(1);
  }

  // Enable the server
  proxyConfig.enabledServers[serverName] = serverConfig;

  // Write updated config
  fs.writeFileSync(proxyConfigPath, JSON.stringify(proxyConfig, null, 2));

  console.log(`✅ Enabled MCP server: ${serverName}`);
  console.log('🔄 Server will be loaded automatically by the proxy');
}

function disableMCP(serverName) {
  const proxyConfigPath = path.join(__dirname, '..', 'mcp-proxy-config.json');

  if (!fs.existsSync(proxyConfigPath)) {
    console.error('❌ Proxy config not found');
    process.exit(1);
  }

  const proxyConfig = JSON.parse(fs.readFileSync(proxyConfigPath, 'utf8'));

  if (!proxyConfig.enabledServers[serverName]) {
    console.log(`ℹ️  Server '${serverName}' is not enabled`);
    return;
  }

  delete proxyConfig.enabledServers[serverName];

  fs.writeFileSync(proxyConfigPath, JSON.stringify(proxyConfig, null, 2));

  console.log(`✅ Disabled MCP server: ${serverName}`);
  console.log('🔄 Server will be unloaded automatically by the proxy');
}

function listMCPs() {
  const proxyConfigPath = path.join(__dirname, '..', 'mcp-proxy-config.json');
  const optionalConfigPath = path.join(__dirname, '..', '..', '.mcp.optional.json');

  let proxyConfig = { enabledServers: {} };
  if (fs.existsSync(proxyConfigPath)) {
    proxyConfig = JSON.parse(fs.readFileSync(proxyConfigPath, 'utf8'));
  }

  let optionalConfig = { mcpServers: {} };
  if (fs.existsSync(optionalConfigPath)) {
    optionalConfig = JSON.parse(fs.readFileSync(optionalConfigPath, 'utf8'));
  }

  const enabled = new Set(Object.keys(proxyConfig.enabledServers));
  const available = new Set(Object.keys(optionalConfig.mcpServers));

  console.log('📊 MCP Server Status:');
  console.log('\n✅ Enabled servers:');
  if (enabled.size === 0) {
    console.log('   (none)');
  } else {
    enabled.forEach(name => {
      console.log(`   - ${name}`);
    });
  }

  console.log('\n💤 Available but disabled:');
  const disabled = [...available].filter(name => !enabled.has(name));
  if (disabled.length === 0) {
    console.log('   (none)');
  } else {
    disabled.forEach(name => {
      console.log(`   - ${name}`);
    });
  }
}

// Command line interface
const [command, serverName] = process.argv.slice(2);

switch (command) {
  case 'enable':
    if (!serverName) {
      console.error('Usage: node mcp-enable.js enable <server-name>');
      process.exit(1);
    }
    enableMCP(serverName);
    break;
  case 'disable':
    if (!serverName) {
      console.error('Usage: node mcp-enable.js disable <server-name>');
      process.exit(1);
    }
    disableMCP(serverName);
    break;
  case 'list':
    listMCPs();
    break;
  default:
    console.log('Usage:');
    console.log('  node mcp-enable.js enable <server-name>   - Enable MCP server');
    console.log('  node mcp-enable.js disable <server-name>  - Disable MCP server');
    console.log('  node mcp-enable.js list                   - List server status');
}