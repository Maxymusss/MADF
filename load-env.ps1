# Load environment variables from .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
        Write-Host "Loaded: $($matches[1])"
    }
}
Write-Host "Environment variables loaded from .env file"