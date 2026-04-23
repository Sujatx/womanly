param(
  [Parameter(Mandatory = $true)]
  [string]$EnvFilePath,

  [string]$OutputDir = "./backups",

  [string]$RetentionDays = "30"
)

$ErrorActionPreference = "Stop"

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

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$backupFile = Join-Path $OutputDir "womanly_$timestamp.sqlc"

$postgresUser = $env:POSTGRES_USER
$postgresDb = $env:POSTGRES_DB
$databaseUrl = $env:DATABASE_URL

if (-not $postgresUser -or -not $postgresDb -or -not $databaseUrl) {
  throw "POSTGRES_USER, POSTGRES_DB, and DATABASE_URL must be present in env file"
}

Write-Host "Creating compressed backup: $backupFile"
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U $postgresUser -d $postgresDb -Fc > $backupFile

Write-Host "Removing backups older than $RetentionDays days"
Get-ChildItem $OutputDir -Filter "womanly_*.sqlc" |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-[int]$RetentionDays) } |
  Remove-Item -Force

Write-Host "Backup complete: $backupFile"
