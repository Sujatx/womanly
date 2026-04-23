param(
  [Parameter(Mandatory = $true)]
  [string]$BackupFile,

  [Parameter(Mandatory = $true)]
  [string]$EnvFilePath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupFile)) {
  throw "Backup file not found: $BackupFile"
}

if (-not (Test-Path $EnvFilePath)) {
  throw "Env file not found: $EnvFilePath"
}

Get-Content $EnvFilePath | ForEach-Object {
  if ($_ -match "^\s*#" -or $_ -match "^\s*$") { return }
  $pair = $_ -split "=", 2
  if ($pair.Count -eq 2) {
    [System.Environment]::SetEnvironmentVariable($pair[0], $pair[1])
  }
}

$postgresUser = $env:POSTGRES_USER
$postgresDb = $env:POSTGRES_DB

if (-not $postgresUser -or -not $postgresDb) {
  throw "POSTGRES_USER and POSTGRES_DB must be present in env file"
}

Write-Host "Restoring backup from $BackupFile into database $postgresDb"
Get-Content -Path $BackupFile -AsByteStream -ReadCount 0 |
  docker compose -f docker-compose.prod.yml exec -T db pg_restore --clean --if-exists -U $postgresUser -d $postgresDb

Write-Host "Restore complete"
