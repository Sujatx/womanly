#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${1:-}"
HEALTH_PATH="${2:-/health}"

if [[ -z "${BASE_URL}" ]]; then
  echo "Usage: $0 <base_url> [health_path]"
  exit 1
fi

if [[ "${BASE_URL}" != https://* ]]; then
  echo "ERROR: BASE_URL must be HTTPS for TLS termination verification: ${BASE_URL}"
  exit 1
fi

TARGET_URL="${BASE_URL%/}${HEALTH_PATH}"
echo "Verifying security headers at: ${TARGET_URL}"

HEADERS=$(curl -fsS -I --proto '=https' --tlsv1.2 "${TARGET_URL}")

require_header() {
  local name="$1"
  if ! grep -iq "^${name}:" <<< "${HEADERS}"; then
    echo "ERROR: Missing required header: ${name}"
    exit 1
  fi
}

require_header "Strict-Transport-Security"
require_header "X-Content-Type-Options"
require_header "X-Frame-Options"
require_header "Content-Security-Policy"
require_header "Referrer-Policy"

echo "Security header verification passed for ${TARGET_URL}"