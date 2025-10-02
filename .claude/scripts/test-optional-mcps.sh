#!/bin/bash
# Test Optional MCP Servers Script
# Tests each optional MCP server by temporarily adding it to .mcp.json

SERVER_NAME=""
ALL_FLAG=false
RESTORE_FLAG=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --server|-s)
            SERVER_NAME="$2"
            shift 2
            ;;
        --all|-a)
            ALL_FLAG=true
            shift
            ;;
        --restore|-r)
            RESTORE_FLAG=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# File paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MCP_JSON="$PROJECT_ROOT/.mcp.json"
MCP_OPTIONAL="$PROJECT_ROOT/.mcp.optional.json"
MCP_BACKUP="$PROJECT_ROOT/.mcp.json.backup"
SETTINGS_JSON="$PROJECT_ROOT/.claude/settings.local.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Backup original .mcp.json
backup_mcp_config() {
    if [[ -f "$MCP_JSON" ]]; then
        cp "$MCP_JSON" "$MCP_BACKUP"
        echo -e "${GREEN}✓ Backed up .mcp.json${NC}"
    fi
}

# Restore original .mcp.json
restore_mcp_config() {
    if [[ -f "$MCP_BACKUP" ]]; then
        cp "$MCP_BACKUP" "$MCP_JSON"
        rm "$MCP_BACKUP"
        echo -e "${GREEN}✓ Restored original .mcp.json${NC}"
        
        # Reset settings to minimal
        reset_settings
        
        echo ""
        echo -e "${YELLOW}Restart Claude Code to use restored configuration${NC}"
    else
        echo -e "${RED}✗ No backup found${NC}"
    fi
}

# Reset settings to minimal essentials
reset_settings() {
    if [[ -f "$SETTINGS_JSON" ]]; then
        # Use node to update JSON properly
        node -e "
        const fs = require('fs');
        const settings = JSON.parse(fs.readFileSync('$SETTINGS_JSON', 'utf8'));
        settings.enabledMcpjsonServers = ['sequential-thinking', 'filesystem'];
        fs.writeFileSync('$SETTINGS_JSON', JSON.stringify(settings, null, 2));
        "
        echo -e "${GREEN}✓ Reset settings to minimal essentials${NC}"
    fi
}

# Add server to .mcp.json
add_mcp_server() {
    local server_name="$1"
    
    echo -e "${CYAN}Testing MCP Server: $server_name${NC}"
    echo "=================================================="
    
    # Check if files exist
    if [[ ! -f "$MCP_JSON" ]] || [[ ! -f "$MCP_OPTIONAL" ]]; then
        echo -e "${RED}✗ Missing config files${NC}"
        return 1
    fi
    
    # Check if server exists in optional using node
    local server_exists=$(node -e "
    try {
        const optional = JSON.parse(require('fs').readFileSync('$MCP_OPTIONAL', 'utf8'));
        console.log(optional.mcpServers['$server_name'] ? 'true' : 'false');
    } catch(e) {
        console.log('false');
    }
    ")
    
    if [[ "$server_exists" != "true" ]]; then
        echo -e "${RED}✗ Server '$server_name' not found in .mcp.optional.json${NC}"
        return 1
    fi
    
    # Merge server into main config using node
    node -e "
    const fs = require('fs');
    try {
        const main = JSON.parse(fs.readFileSync('$MCP_JSON', 'utf8'));
        const optional = JSON.parse(fs.readFileSync('$MCP_OPTIONAL', 'utf8'));
        
        main.mcpServers['$server_name'] = optional.mcpServers['$server_name'];
        fs.writeFileSync('$MCP_JSON', JSON.stringify(main, null, 2));
        console.log('success');
    } catch(e) {
        console.log('error');
    }
    "
    
    # Update settings to enable the server
    if [[ -f "$SETTINGS_JSON" ]]; then
        node -e "
        const fs = require('fs');
        try {
            const settings = JSON.parse(fs.readFileSync('$SETTINGS_JSON', 'utf8'));
            if (!settings.enabledMcpjsonServers.includes('$server_name')) {
                settings.enabledMcpjsonServers.push('$server_name');
            }
            fs.writeFileSync('$SETTINGS_JSON', JSON.stringify(settings, null, 2));
        } catch(e) {}
        "
    fi
    
    echo -e "${GREEN}✓ Added $server_name to .mcp.json and settings${NC}"
    echo ""
    echo -e "${YELLOW}NEXT STEPS:${NC}"
    echo -e "${WHITE}1. Restart Claude Code to load the server${NC}"
    echo -e "${WHITE}2. Run '/context' to verify server loaded successfully${NC}"
    echo -e "${WHITE}3. Test server functionality${NC}"
    echo -e "${WHITE}4. Run this script with --restore to clean up when done${NC}"
    echo ""
    
    # Show server details
    echo -e "${MAGENTA}Server Configuration:${NC}"
    node -e "
    const optional = JSON.parse(require('fs').readFileSync('$MCP_OPTIONAL', 'utf8'));
    console.log(JSON.stringify(optional.mcpServers['$server_name'], null, 2));
    "
    
    return 0
}

# List all optional servers
list_optional_servers() {
    if [[ ! -f "$MCP_OPTIONAL" ]]; then
        echo -e "${RED}✗ .mcp.optional.json not found${NC}"
        return
    fi
    
    echo -e "${CYAN}Available Optional MCP Servers:${NC}"
    echo "========================================"
    
    node -e "
    const optional = JSON.parse(require('fs').readFileSync('$MCP_OPTIONAL', 'utf8'));
    for (const [name, config] of Object.entries(optional.mcpServers)) {
        console.log(\`• \${name}\`);
        console.log(\`  Command: \${config.command} \${(config.args || []).join(' ')}\`);
        if (config.env && Object.keys(config.env).length > 0) {
            console.log(\`  Env vars: \${Object.keys(config.env).join(', ')}\`);
        }
        console.log('');
    }
    "
}

# Main script logic
if [[ "$RESTORE_FLAG" == "true" ]]; then
    restore_mcp_config
    exit 0
fi

if [[ "$ALL_FLAG" == "true" ]]; then
    echo -e "${YELLOW}Testing all optional MCP servers is not recommended.${NC}"
    echo -e "${YELLOW}This would load many tools and consume significant context tokens.${NC}"
    echo -e "${WHITE}Instead, test servers one by one using: ./test-optional-mcps.sh --server <name>${NC}"
    echo ""
    list_optional_servers
    exit 0
fi

if [[ -z "$SERVER_NAME" ]]; then
    echo -e "${CYAN}MCP Server Testing Tool${NC}"
    echo "=============================="
    echo ""
    echo "Usage:"
    echo "  ./test-optional-mcps.sh --server <server-name>    # Test specific server"
    echo "  ./test-optional-mcps.sh --all                     # Show all available servers"
    echo "  ./test-optional-mcps.sh --restore                 # Restore original config"
    echo ""
    list_optional_servers
    exit 0
fi

# Test specific server
backup_mcp_config
if add_mcp_server "$SERVER_NAME"; then
    echo -e "${GREEN}Server configuration updated successfully!${NC}"
else
    echo -e "${RED}Failed to configure server${NC}"
    restore_mcp_config
fi