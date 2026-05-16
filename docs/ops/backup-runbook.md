# Backup and Restore Runbook

## Scope

This runbook covers PostgreSQL backup and restore for the production compose stack.

## Daily backup

Run:

powershell -ExecutionPolicy Bypass -File ./scripts/backup_db.ps1 -EnvFilePath ./.env.prod

Or on Linux hosts:

bash ./scripts/backup_db.sh ./.env.prod ./backups 30

Schedule this via cron or CI on your host.

Behavior:
- Produces compressed backup files in backups/
- File name format: womanly_YYYYMMDD_HHMMSS.sqlc
- Removes backups older than 30 days
- Generates SHA256 checksum file alongside each backup
- If BACKUP_UPLOAD_COMMAND is set, runs off-site upload step (expected to target encrypted object storage)

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

Recommended BACKUP_UPLOAD_COMMAND examples:

- AWS S3 (SSE-S3):
	aws s3 cp "$BACKUP_FILE" "s3://your-bucket/womanly/" --sse AES256

- AWS S3 (KMS):
	aws s3 cp "$BACKUP_FILE" "s3://your-bucket/womanly/" --sse aws:kms --sse-kms-key-id "$KMS_KEY_ID"

- Azure Blob (customer-managed key/container policy enforced at storage account):
	az storage blob upload --account-name "$AZ_ACCOUNT" --container-name "$AZ_CONTAINER" --name "$(basename "$BACKUP_FILE")" --file "$BACKUP_FILE" --auth-mode login

## Evidence and audit

- Keep the .sha256 checksum alongside each backup
- Record timestamp, operator, backup file, and storage location
- For release signoff, use docs/ops/release-evidence-template.md and attach logs

## Incident notes

Record every restore drill or real recovery event with:
- Date/time
- Operator
- Backup file used
- Recovery duration
- Validation result
