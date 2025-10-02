#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function setupMCPProxy() {
  const mcpConfigPath = path.join(__dirname, '..', '..', '.mcp.json');
  const proxyConfigPath = path.join(__dirname, '..', 'mcp-proxy-config.json');

  // Backup original config
  const backupPath = mcpConfigPath + '.before-proxy';
  if (fs.existsSync(mcpConfigPath) && !fs.existsSync(backupPath)) {
    fs.copyFileSync(mcpConfigPath, backupPath);
    console.log('✅ Backed up original .mcp.json');
  }

  // Create new config that only loads the proxy
  const proxyConfig = {
    mcpServers: {
      "sequential-thinking": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
      },
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
        "env": {
          "HOME_DIR": "${USERPROFILE}"
        }
      },
      "obsidian": {
        "command": "uvx",
        "args": ["mcp-obsidian"],
        "env": {
          "OBSIDIAN_API_KEY": "${OBSIDIAN_API_KEY}",
          "OBSIDIAN_HOST": "${OBSIDIAN_HOST}",
          "OBSIDIAN_PORT": "${OBSIDIAN_PORT}"
        }
      },
      "mcp-proxy": {
        "command": "node",
        "args": [".claude/mcp-proxy/proxy-server.js"]
      }
    }
  };

  fs.writeFileSync(mcpConfigPath, JSON.stringify(proxyConfig, null, 2));
  console.log('✅ Updated .mcp.json to use proxy server');

  // Initialize proxy config if it doesn't exist
  if (!fs.existsSync(proxyConfigPath)) {
    const initialProxyConfig = {
      enabledServers: {}
    };
    fs.writeFileSync(proxyConfigPath, JSON.stringify(initialProxyConfig, null, 2));
    console.log('✅ Created initial proxy configuration');
  }

  console.log('\n🚀 MCP Proxy setup complete!');
  console.log('📋 Next steps:');
  console.log('   1. Restart Claude Code to load the proxy');
  console.log('   2. Use mcp_proxy__* tools to manage servers dynamically');
  console.log('   3. Run node .claude/scripts/mcp-enable.js <server-name> to enable servers');
}

function restoreOriginal() {
  const mcpConfigPath = path.join(__dirname, '..', '..', '.mcp.json');
  const backupPath = mcpConfigPath + '.before-proxy';

  if (fs.existsSync(backupPath)) {
    fs.copyFileSync(backupPath, mcpConfigPath);
    console.log('✅ Restored original .mcp.json');
  } else {
    console.log('❌ No backup found');
  }
}

// Command line interface
const command = process.argv[2];

switch (command) {
  case 'setup':
    setupMCPProxy();
    break;
  case 'restore':
    restoreOriginal();
    break;
  default:
    console.log('Usage:');
    console.log('  node setup-mcp-proxy.js setup   - Setup proxy system');
    console.log('  node setup-mcp-proxy.js restore - Restore original config');
}