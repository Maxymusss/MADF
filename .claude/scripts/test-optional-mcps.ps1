#!/usr/bin/env pwsh
# Test Optional MCP Servers Script
# Tests each optional MCP server by temporarily adding it to .mcp.json

param(
    [string]$ServerName = "",
    [switch]$All = $false,
    [switch]$Restore = $false
)

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# File paths
$McpJsonPath = Join-Path $ProjectRoot ".mcp.json"
$McpOptionalPath = Join-Path $ProjectRoot ".mcp.optional.json"
$McpBackupPath = Join-Path $ProjectRoot ".mcp.json.backup"
$SettingsPath = Join-Path $ProjectRoot ".claude\settings.local.json"

# Backup original .mcp.json
function Backup-McpConfig {
    if (Test-Path $McpJsonPath) {
        Copy-Item $McpJsonPath $McpBackupPath -Force
        Write-Host "✓ Backed up .mcp.json" -ForegroundColor Green
    }
}

# Restore original .mcp.json
function Restore-McpConfig {
    if (Test-Path $McpBackupPath) {
        Copy-Item $McpBackupPath $McpJsonPath -Force
        Remove-Item $McpBackupPath -Force
        Write-Host "✓ Restored original .mcp.json" -ForegroundColor Green
        
        # Reset settings to minimal
        Reset-Settings
        
        Write-Host ""
        Write-Host "Restart Claude Code to use restored configuration" -ForegroundColor Yellow
    } else {
        Write-Host "✗ No backup found" -ForegroundColor Red
    }
}

# Reset settings to minimal essentials
function Reset-Settings {
    if (Test-Path $SettingsPath) {
        $settings = Get-Content $SettingsPath -Raw | ConvertFrom-Json
        $settings.enabledMcpjsonServers = @("sequential-thinking", "filesystem")
        $settings | ConvertTo-Json -Depth 10 | Set-Content $SettingsPath
        Write-Host "✓ Reset settings to minimal essentials" -ForegroundColor Green
    }
}

# Add server to .mcp.json
function Add-McpServer {
    param([string]$ServerName)
    
    Write-Host "Testing MCP Server: $ServerName" -ForegroundColor Cyan
    Write-Host "=" * 50
    
    # Read configs
    if (!(Test-Path $McpJsonPath) -or !(Test-Path $McpOptionalPath)) {
        Write-Host "✗ Missing config files" -ForegroundColor Red
        return $false
    }
    
    $mainConfig = Get-Content $McpJsonPath -Raw | ConvertFrom-Json
    $optionalConfig = Get-Content $McpOptionalPath -Raw | ConvertFrom-Json
    
    # Check if server exists in optional
    if (!$optionalConfig.mcpServers.$ServerName) {
        Write-Host "✗ Server '$ServerName' not found in .mcp.optional.json" -ForegroundColor Red
        return $false
    }
    
    # Add server to main config
    $mainConfig.mcpServers | Add-Member -NotePropertyName $ServerName -NotePropertyValue $optionalConfig.mcpServers.$ServerName -Force
    
    # Save updated config
    $mainConfig | ConvertTo-Json -Depth 10 | Set-Content $McpJsonPath
    
    # Update settings to enable the server
    if (Test-Path $SettingsPath) {
        $settings = Get-Content $SettingsPath -Raw | ConvertFrom-Json
        if ($settings.enabledMcpjsonServers -notcontains $ServerName) {
            $settings.enabledMcpjsonServers = @($settings.enabledMcpjsonServers) + @($ServerName)
        }
        $settings | ConvertTo-Json -Depth 10 | Set-Content $SettingsPath
    }
    
    Write-Host "✓ Added $ServerName to .mcp.json and settings" -ForegroundColor Green
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Restart Claude Code to load the server" -ForegroundColor White
    Write-Host "2. Run '/context' to verify server loaded successfully" -ForegroundColor White
    Write-Host "3. Test server functionality" -ForegroundColor White
    Write-Host "4. Run this script with -Restore to clean up when done" -ForegroundColor White
    Write-Host ""
    
    # Show server details
    Write-Host "Server Configuration:" -ForegroundColor Magenta
    $optionalConfig.mcpServers.$ServerName | ConvertTo-Json -Depth 5
    
    return $true
}

# List all optional servers
function List-OptionalServers {
    if (!(Test-Path $McpOptionalPath)) {
        Write-Host "✗ .mcp.optional.json not found" -ForegroundColor Red
        return
    }
    
    $optionalConfig = Get-Content $McpOptionalPath -Raw | ConvertFrom-Json
    
    Write-Host "Available Optional MCP Servers:" -ForegroundColor Cyan
    Write-Host "=" * 40
    
    $optionalConfig.mcpServers.PSObject.Properties | ForEach-Object {
        $name = $_.Name
        $config = $_.Value
        Write-Host "• $name" -ForegroundColor Green
        Write-Host "  Command: $($config.command) $($config.args -join ' ')" -ForegroundColor Gray
        if ($config.env -and $config.env.PSObject.Properties.Count -gt 0) {
            Write-Host "  Env vars: $($config.env.PSObject.Properties.Name -join ', ')" -ForegroundColor Gray
        }
        Write-Host ""
    }
}

# Main script logic
if ($Restore) {
    Restore-McpConfig
    exit 0
}

if ($All) {
    Write-Host "Testing all optional MCP servers is not recommended." -ForegroundColor Yellow
    Write-Host "This would load many tools and consume significant context tokens." -ForegroundColor Yellow
    Write-Host "Instead, test servers one by one using: .\test-optional-mcps.ps1 -ServerName <name>" -ForegroundColor White
    Write-Host ""
    List-OptionalServers
    exit 0
}

if ($ServerName -eq "") {
    Write-Host "MCP Server Testing Tool" -ForegroundColor Cyan
    Write-Host "=" * 30
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\test-optional-mcps.ps1 -ServerName <server-name>    # Test specific server"
    Write-Host "  .\test-optional-mcps.ps1 -All                        # Show all available servers"
    Write-Host "  .\test-optional-mcps.ps1 -Restore                    # Restore original config"
    Write-Host ""
    List-OptionalServers
    exit 0
}

# Test specific server
Backup-McpConfig
if (Add-McpServer -ServerName $ServerName) {
    Write-Host "Server configuration updated successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to configure server" -ForegroundColor Red
    Restore-McpConfig
}