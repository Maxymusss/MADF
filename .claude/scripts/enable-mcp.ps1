# Enable MCP Server Script
# Temporarily adds servers from .mcp.optional.json for current session

param(
    [Parameter(Mandatory=$true)]
    [string[]]$Servers,
    
    [switch]$List,
    [switch]$Restore,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Enable MCP Servers - Temporary Session Tool

USAGE:
  .\enable-mcp.ps1 task-master-ai           # Enable Task Master
  .\enable-mcp.ps1 context7                 # Enable research tools
  .\enable-mcp.ps1 github,context7          # Enable multiple servers
  .\enable-mcp.ps1 -List                    # Show available servers
  .\enable-mcp.ps1 -Restore                 # Restore minimal default
  
EXAMPLES:
  .\enable-mcp.ps1 task-master-ai           # Add task management
  .\enable-mcp.ps1 context7,github          # Add research + GitHub
  
NOTE: Restart Claude Code after running to apply changes
"@
    return
}

$mcpPath = ".mcp.json"
$optionalPath = ".mcp.optional.json"
$settingsPath = ".claude/settings.local.json"
$backupPath = ".mcp.json.backup"

# List available servers
if ($List) {
    Write-Host "Available MCP Servers:" -ForegroundColor Cyan
    
    if (Test-Path $optionalPath) {
        $optional = Get-Content $optionalPath | ConvertFrom-Json
        foreach ($server in $optional.mcpServers.PSObject.Properties.Name) {
            Write-Host "  $server" -ForegroundColor Green
        }
    }
    
    Write-Host "`nCurrently enabled:" -ForegroundColor Yellow
    if (Test-Path $settingsPath) {
        $settings = Get-Content $settingsPath | ConvertFrom-Json
        foreach ($server in $settings.enabledMcpjsonServers) {
            Write-Host "  $server" -ForegroundColor White
        }
    }
    return
}

# Restore minimal configuration
if ($Restore) {
    Write-Host "Restoring minimal configuration..." -ForegroundColor Yellow
    
    if (Test-Path $backupPath) {
        Copy-Item $backupPath $mcpPath -Force
        Remove-Item $backupPath -Force
    } else {
        # Recreate minimal config
        $minimalConfig = @{
            mcpServers = @{
                "sequential-thinking" = @{
                    command = "npx"
                    args = @("-y", "@modelcontextprotocol/server-sequential-thinking")
                }
                "filesystem" = @{
                    command = "npx"
                    args = @("-y", "@modelcontextprotocol/server-filesystem", (Get-Location).Path)
                    env = @{
                        "HOME_DIR" = "`${USERPROFILE}"
                    }
                }
            }
        }
        $minimalConfig | ConvertTo-Json -Depth 10 | Set-Content $mcpPath
    }
    
    # Update settings
    if (Test-Path $settingsPath) {
        $settings = Get-Content $settingsPath | ConvertFrom-Json
        $settings.enabledMcpjsonServers = @("sequential-thinking", "filesystem")
        $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
    }
    
    Write-Host "Restored to minimal configuration (sequential-thinking, filesystem)" -ForegroundColor Green
    Write-Host "Restart Claude Code to apply changes" -ForegroundColor Cyan
    return
}

# Enable specified servers
if (-not (Test-Path $optionalPath)) {
    Write-Error "Optional servers file not found: $optionalPath"
    return
}

if (-not (Test-Path $mcpPath)) {
    Write-Error "Main MCP config not found: $mcpPath"
    return
}

# Backup current config
Copy-Item $mcpPath $backupPath -Force

# Load configurations
$mainConfig = Get-Content $mcpPath | ConvertFrom-Json
$optionalConfig = Get-Content $optionalPath | ConvertFrom-Json

# Add requested servers
$addedServers = @()
foreach ($serverName in $Servers) {
    if ($optionalConfig.mcpServers.PSObject.Properties.Name -contains $serverName) {
        $mainConfig.mcpServers | Add-Member -NotePropertyName $serverName -NotePropertyValue $optionalConfig.mcpServers.$serverName -Force
        $addedServers += $serverName
        Write-Host "Added: $serverName" -ForegroundColor Green
    } else {
        Write-Warning "Server not found in optional config: $serverName"
    }
}

if ($addedServers.Count -eq 0) {
    Write-Host "No servers were added" -ForegroundColor Yellow
    Remove-Item $backupPath -Force
    return
}

# Save updated main config
$mainConfig | ConvertTo-Json -Depth 10 | Set-Content $mcpPath

# Update settings to enable the servers
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath | ConvertFrom-Json
    $currentEnabled = [System.Collections.ArrayList]$settings.enabledMcpjsonServers
    
    foreach ($server in $addedServers) {
        if (-not $currentEnabled.Contains($server)) {
            $currentEnabled.Add($server) | Out-Null
        }
    }
    
    $settings.enabledMcpjsonServers = $currentEnabled.ToArray()
    $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
}

Write-Host "`nEnabled servers: $($addedServers -join ', ')" -ForegroundColor Cyan
Write-Host "Restart Claude Code to apply changes" -ForegroundColor Yellow
Write-Host "`nTo restore minimal config: .\enable-mcp.ps1 -Restore" -ForegroundColor Gray