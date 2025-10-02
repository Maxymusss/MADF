param(
  [switch]$Execute,
  [switch]$IncludeProjectConfigs,
  [string]$ProjectRoot = "D:\dev\MADF",
  [string]$BackupDir = "$env:USERPROFILE\Desktop\claude-reset-backup-$(Get-Date -Format yyyyMMdd-HHmmss)"
)

$dryRun = -not $Execute

function Write-Section($title) {
  Write-Host "`n=== $title ===" -ForegroundColor Cyan
}

function Warn($msg) {
  Write-Host "[WARN] $msg" -ForegroundColor Yellow
}

function Info($msg) {
  Write-Host "[INFO] $msg" -ForegroundColor Gray
}

function Remove-IfExists {
  param(
    [Parameter(Mandatory=$true)][string]$Path
  )
  if (Test-Path -LiteralPath $Path) {
    if ($dryRun) {
      Info "Would remove: $Path"
      Remove-Item -LiteralPath $Path -Recurse -Force -WhatIf | Out-Null
    } else {
      Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue
      Info "Removed: $Path"
    }
  }
}

function Copy-IfExists {
  param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$Destination
  )
  if (Test-Path -LiteralPath $Source) {
    if ($dryRun) {
      Info "Would back up: $Source -> $Destination"
    } else {
      New-Item -ItemType Directory -Path (Split-Path -LiteralPath $Destination) -Force | Out-Null
      Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force -ErrorAction SilentlyContinue
      Info "Backed up: $Source -> $Destination"
    }
  }
}

function Get-FolderSizeKB {
  param([string]$Path)
  if (!(Test-Path -LiteralPath $Path)) { return 0 }
  try {
    return "{0:N0}" -f ((Get-ChildItem -LiteralPath $Path -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1KB)
  } catch { return 0 }
}

Write-Section "Process check"
$procNames = @("Code","Code - Insiders","Cursor")
$running = Get-Process -ErrorAction SilentlyContinue | Where-Object { $procNames -contains $_.ProcessName } | Select-Object -ExpandProperty ProcessName -Unique
if ($running) {
  Warn "Detected running editors: $($running -join ', '). Please close them for a clean reset."
} else {
  Info "No running VS Code/Cursor processes detected."
}

# Targets for VS Code and Cursor
$targets = @(
  @{
    Name = "VS Code"
    ExtDir = Join-Path $env:USERPROFILE ".vscode\extensions"
    StorageDir = Join-Path $env:APPDATA "Code\User\globalStorage"
  },
  @{
    Name = "Cursor"
    ExtDir = Join-Path $env:USERPROFILE ".cursor\extensions"
    StorageDir = Join-Path $env:APPDATA "Cursor\User\globalStorage"
  }
)

# Build deletion list: Anthropic/Claude extension folders + global storage
$deleteList = @()

foreach ($t in $targets) {
  if (Test-Path -LiteralPath $t.ExtDir) {
    # Common publisher prefix is "anthropic"
    $exts = Get-ChildItem -LiteralPath $t.ExtDir -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -like "anthropic*" }
    foreach ($e in $exts) {
      $deleteList += @{
        Kind = "Extension"
        Editor = $t.Name
        Path = $e.FullName
        SizeKB = (Get-FolderSizeKB -Path $e.FullName)
      }
    }
  }
  if (Test-Path -LiteralPath $t.StorageDir) {
    $stor = Get-ChildItem -LiteralPath $t.StorageDir -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -like "anthropic*" }
    foreach ($s in $stor) {
      $deleteList += @{
        Kind = "GlobalStorage"
        Editor = $t.Name
        Path = $s.FullName
        SizeKB = (Get-FolderSizeKB -Path $s.FullName)
      }
    }
  }
}

Write-Section "Planned removals (Anthropic/Claude footprints)"
if ($deleteList.Count -eq 0) {
  Info "No Anthropic/Claude-related folders found in extensions/globalStorage."
} else {
  foreach ($item in $deleteList) {
    Write-Host ("{0,-12} | {1,-8} | {2,8} KB | {3}" -f $item.Kind, $item.Editor, $item.SizeKB, $item.Path)
  }
}

# Optional: project-level configs
$projectDeletes = @()
if ($IncludeProjectConfigs) {
  $candidates = @(
    Join-Path $ProjectRoot ".claude\settings.local.json",
    Join-Path $ProjectRoot ".mcp.json"
  )
  foreach ($c in $candidates) {
    if (Test-Path -LiteralPath $c) {
      $projectDeletes += $c
    }
  }
  Write-Section "Project config candidates"
  if ($projectDeletes.Count -eq 0) {
    Info "No project config files found to reset."
  } else {
    foreach ($p in $projectDeletes) {
      Write-Host ("{0} (size ~{1} KB)" -f $p, (Get-FolderSizeKB -Path $p))
    }
    if (-not $dryRun) {
      Write-Section "Backing up project configs"
      foreach ($p in $projectDeletes) {
        $rel = $p.Substring($ProjectRoot.Length).TrimStart('\\','/')
        $dest = Join-Path $BackupDir ("project-config-backup" + $rel.Replace('\\','/'))
        Copy-IfExists -Source $p -Destination $dest
      }
    } else {
      Info "Would back up project configs to: $BackupDir"
    }
  }
}

# Execute removals
Write-Section ($(if($dryRun){"DRY RUN (no changes)"} else {"EXECUTION (files will be deleted)"}))
foreach ($item in $deleteList) {
  Remove-IfExists -Path $item.Path
}
if ($IncludeProjectConfigs -and $projectDeletes.Count -gt 0) {
  foreach ($p in $projectDeletes) {
    Remove-IfExists -Path $p
  }
}

Write-Section "Next steps"
if ($dryRun) {
  Write-Host "Review the list above. Re-run with -Execute to apply." -ForegroundColor Green
} else {
  Write-Host "Done. Reinstall 'Claude Code' in your editor and sign in again." -ForegroundColor Green
  Write-Host "If project configs were included, backups are in: $BackupDir" -ForegroundColor Green
}



