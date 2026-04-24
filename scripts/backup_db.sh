#!/usr/bin/env bash

set -euo pipefail

ENV_FILE_PATH="${1:-}"
OUTPUT_DIR="${2:-./backups}"
RETENTION_DAYS="${3:-30}"

if [[ -z "${ENV_FILE_PATH}" ]]; then
  echo "Usage: $0 <env_file_path> [output_dir] [retention_days]"
  exit 1
fi

if [[ ! -f "${ENV_FILE_PATH}" ]]; then
  echo "Env file not found: ${ENV_FILE_PATH}"
  exit 1
fi

set -a
source "${ENV_FILE_PATH}"
set +a

if [[ -z "${POSTGRES_USER:-}" || -z "${POSTGRES_DB:-}" ]]; then
  echo "POSTGRES_USER and POSTGRES_DB must be present in env file"
  exit 1
fi

mkdir -p "${OUTPUT_DIR}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="${OUTPUT_DIR}/womanly_${TIMESTAMP}.sqlc"

echo "Creating compressed backup: ${BACKUP_FILE}"
docker compose -f docker-compose.prod.yml --env-file "${ENV_FILE_PATH}" exec -T db \
  pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Fc > "${BACKUP_FILE}"

echo "Removing backups older than ${RETENTION_DAYS} days"
find "${OUTPUT_DIR}" -type f -name 'womanly_*.sqlc' -mtime +"${RETENTION_DAYS}" -delete

if [[ -n "${BACKUP_UPLOAD_COMMAND:-}" ]]; then
  echo "Uploading backup to external encrypted storage via BACKUP_UPLOAD_COMMAND"
  export BACKUP_FILE
  bash -lc "${BACKUP_UPLOAD_COMMAND}"
fi

sha256sum "${BACKUP_FILE}" > "${BACKUP_FILE}.sha256"
echo "Backup complete: ${BACKUP_FILE}"