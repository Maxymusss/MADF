#!/bin/bash
# Enable MCP Server Script
# Temporarily adds servers from .mcp.optional.json for current session

show_help() {
    cat << EOF
Enable MCP Servers - Temporary Session Tool

USAGE:
  ./enable-mcp.sh task-master-ai           # Enable Task Master
  ./enable-mcp.sh context7                 # Enable research tools
  ./enable-mcp.sh "github context7"        # Enable multiple servers
  ./enable-mcp.sh --list                   # Show available servers
  ./enable-mcp.sh --restore                # Restore minimal default
  
EXAMPLES:
  ./enable-mcp.sh task-master-ai           # Add task management
  ./enable-mcp.sh "context7 github"        # Add research + GitHub
  
NOTE: Restart Claude Code after running to apply changes
EOF
}

list_servers() {
    echo "Available MCP Servers:"
    if [[ -f ".mcp.optional.json" ]]; then
        jq -r '.mcpServers | keys[]' .mcp.optional.json | sed 's/^/  /'
    fi
    
    echo ""
    echo "Currently enabled:"
    if [[ -f ".claude/settings.local.json" ]]; then
        jq -r '.enabledMcpjsonServers[]' .claude/settings.local.json | sed 's/^/  /'
    fi
}

restore_minimal() {
    echo "Restoring minimal configuration..."
    
    if [[ -f ".mcp.json.backup" ]]; then
        mv .mcp.json.backup .mcp.json
    else
        # Recreate minimal config
        cat > .mcp.json << 'EOF'
{
	"mcpServers": {
		"sequential-thinking": {
			"command": "npx",
			"args": [
				"-y",
				"@modelcontextprotocol/server-sequential-thinking"
			]
		},
		"filesystem": {
			"command": "npx",
			"args": [
				"-y",
				"@modelcontextprotocol/server-filesystem",
				"$(pwd)"
			],
			"env": {
				"HOME_DIR": "${HOME}"
			}
		}
	}
}
EOF
    fi
    
    # Update settings
    if [[ -f ".claude/settings.local.json" ]]; then
        jq '.enabledMcpjsonServers = ["sequential-thinking", "filesystem"]' .claude/settings.local.json > .claude/settings.local.json.tmp
        mv .claude/settings.local.json.tmp .claude/settings.local.json
    fi
    
    echo "Restored to minimal configuration (sequential-thinking, filesystem)"
    echo "Restart Claude Code to apply changes"
}

# Parse arguments
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    --list|-l)
        list_servers
        exit 0
        ;;
    --restore|-r)
        restore_minimal
        exit 0
        ;;
    "")
        echo "Error: No servers specified"
        show_help
        exit 1
        ;;
esac

# Check required files
if [[ ! -f ".mcp.optional.json" ]]; then
    echo "Error: Optional servers file not found: .mcp.optional.json"
    exit 1
fi

if [[ ! -f ".mcp.json" ]]; then
    echo "Error: Main MCP config not found: .mcp.json"
    exit 1
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    exit 1
fi

# Backup current config
cp .mcp.json .mcp.json.backup

# Parse requested servers
IFS=' ' read -ra SERVERS <<< "$1"
added_servers=()

# Add each requested server
for server in "${SERVERS[@]}"; do
    if jq -e ".mcpServers.\"$server\"" .mcp.optional.json > /dev/null 2>&1; then
        # Extract server config and add to main config
        server_config=$(jq ".mcpServers.\"$server\"" .mcp.optional.json)
        jq --argjson config "$server_config" ".mcpServers.\"$server\" = \$config" .mcp.json > .mcp.json.tmp
        mv .mcp.json.tmp .mcp.json
        added_servers+=("$server")
        echo "Added: $server"
    else
        echo "Warning: Server not found in optional config: $server"
    fi
done

if [[ ${#added_servers[@]} -eq 0 ]]; then
    echo "No servers were added"
    rm .mcp.json.backup
    exit 0
fi

# Update settings to enable the servers
if [[ -f ".claude/settings.local.json" ]]; then
    current_servers=$(jq -r '.enabledMcpjsonServers[]' .claude/settings.local.json)
    all_servers=($current_servers "${added_servers[@]}")
    
    # Remove duplicates and create JSON array
    unique_servers=($(printf '%s\n' "${all_servers[@]}" | sort -u))
    servers_json=$(printf '%s\n' "${unique_servers[@]}" | jq -R . | jq -s .)
    
    jq --argjson servers "$servers_json" '.enabledMcpjsonServers = $servers' .claude/settings.local.json > .claude/settings.local.json.tmp
    mv .claude/settings.local.json.tmp .claude/settings.local.json
fi

echo ""
echo "Enabled servers: ${added_servers[*]}"
echo "Restart Claude Code to apply changes"
echo ""
echo "To restore minimal config: ./enable-mcp.sh --restore"