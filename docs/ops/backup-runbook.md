# Backup and Restore Runbook

## Scope

This runbook covers PostgreSQL backup and restore for the production compose stack.

## Daily backup

Run:

powershell -ExecutionPolicy Bypass -File ./scripts/backup_db.ps1 -EnvFilePath ./.env.prod

Behavior:
- Produces compressed backup files in backups/
- File name format: womanly_YYYYMMDD_HHMMSS.sqlc
- Removes backups older than 30 days

## Restore drill (monthly)

Run:

powershell -ExecutionPolicy Bypass -File ./scripts/restore_db.ps1 -BackupFile ./backups/womanly_YYYYMMDD_HHMMSS.sqlc -EnvFilePath ./.env.prod

Checklist:
- Confirm application maintenance window
- Stop write traffic during restore
- Validate key tables and row counts after restore
- Capture restore duration and errors

## Off-site retention

After backup creation, copy files to encrypted object storage (S3/GCS/Azure Blob) with lifecycle retention policy.

## Incident notes

Record every restore drill or real recovery event with:
- Date/time
- Operator
- Backup file used
- Recovery duration
- Validation result
