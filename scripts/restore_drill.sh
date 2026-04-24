#!/usr/bin/env bash

set -euo pipefail

ENV_FILE_PATH="${1:-}"
BACKUP_DIR="${2:-./backups}"
BACKUP_FILE_OVERRIDE="${3:-}"

if [[ -z "${ENV_FILE_PATH}" ]]; then
  echo "Usage: $0 <env_file_path> [backup_dir] [backup_file_override]"
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

if [[ -n "${BACKUP_FILE_OVERRIDE}" ]]; then
  BACKUP_FILE="${BACKUP_FILE_OVERRIDE}"
else
  BACKUP_FILE=$(ls -1t "${BACKUP_DIR}"/womanly_*.sqlc 2>/dev/null | head -n 1 || true)
fi

if [[ -z "${BACKUP_FILE:-}" || ! -f "${BACKUP_FILE}" ]]; then
  echo "No backup file found for restore drill"
  exit 1
fi

START_TS=$(date +%s)
START_HUMAN=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "Running restore drill with backup: ${BACKUP_FILE}"
cat "${BACKUP_FILE}" | docker compose -f docker-compose.prod.yml --env-file "${ENV_FILE_PATH}" exec -T db \
  pg_restore --clean --if-exists -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"

USERS_COUNT=$(docker compose -f docker-compose.prod.yml --env-file "${ENV_FILE_PATH}" exec -T db \
  psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -tAc "SELECT COUNT(*) FROM \"user\";")
PRODUCTS_COUNT=$(docker compose -f docker-compose.prod.yml --env-file "${ENV_FILE_PATH}" exec -T db \
  psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -tAc "SELECT COUNT(*) FROM product;")
ORDERS_COUNT=$(docker compose -f docker-compose.prod.yml --env-file "${ENV_FILE_PATH}" exec -T db \
  psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -tAc "SELECT COUNT(*) FROM \"order\";")

END_TS=$(date +%s)
DURATION_SEC=$((END_TS - START_TS))
END_HUMAN=$(date -u +%Y-%m-%dT%H:%M:%SZ)

EVIDENCE_FILE="${BACKUP_DIR}/restore-drill-evidence.txt"
{
  echo "started_at=${START_HUMAN}"
  echo "ended_at=${END_HUMAN}"
  echo "duration_seconds=${DURATION_SEC}"
  echo "backup_file=${BACKUP_FILE}"
  echo "users_count=${USERS_COUNT}"
  echo "products_count=${PRODUCTS_COUNT}"
  echo "orders_count=${ORDERS_COUNT}"
  echo "result=success"
} > "${EVIDENCE_FILE}"

echo "Restore drill complete: ${EVIDENCE_FILE}"