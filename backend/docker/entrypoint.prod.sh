#!/bin/sh
set -eu

# Populate selected environment variables from Docker secrets files.
load_secret() {
  var_name="$1"
  file_var="${var_name}_FILE"
  file_path="$(printenv "$file_var" || true)"

  if [ -n "$file_path" ] && [ -f "$file_path" ]; then
    export "$var_name=$(cat "$file_path")"
  fi
}

load_secret "POSTGRES_PASSWORD"
load_secret "SECRET_KEY"
load_secret "SMTP_PASSWORD"
load_secret "SENTRY_DSN"
load_secret "RAZORPAY_KEY_ID"
load_secret "RAZORPAY_KEY_SECRET"

exec "$@"
