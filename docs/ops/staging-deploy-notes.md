# Staging Deployment Notes

## Goal

Deploy main branch changes automatically to staging after CI checks and image build pass.

## Current baseline

- GitHub Actions workflow exists at .github/workflows/ci-cd.yml
- build-images publishes immutable backend/frontend images to GHCR
- deploy-staging job deploys over SSH using docker compose with those immutable tags
- post-deploy smoke test checks /health on staging
- post-deploy gate verifies TLS + required security headers on /health
- CI uploads staging-security-headers artifact for release evidence

## Required repository/environment secrets

- STAGING_SSH_HOST
- STAGING_SSH_PORT (optional; defaults to 22)
- STAGING_SSH_USER
- STAGING_SSH_KEY
- STAGING_APP_DIR (absolute path of checked-out repo on staging host)
- STAGING_PUBLIC_BASE_URL (for smoke test; example: https://staging.womanly.com)
- STAGING_ENV_FILE (optional; defaults to .env.staging)
- STAGING_BACKUP_DIR (optional; defaults to backups)
- STAGING_BACKUP_RETENTION_DAYS (optional; defaults to 30)
- BACKUP_UPLOAD_COMMAND (required by daily backup workflow; should upload with encryption)
- RESTORE_DRILL_BACKUP_FILE (optional; specific backup path for drill; defaults to latest)

## Staging host requirements

1. Repo checked out at STAGING_APP_DIR and kept up to date with main branch
2. Docker + Compose v2 available on host
3. .env.staging present (same shape as .env.prod)
4. secrets/ files present for compose secrets mount
5. Host logged in to GHCR with pull permission for published images

## Optional next steps

1. Add extended smoke tests (auth + cart + checkout sanity)
2. Add rollback step based on previous IMAGE_TAG
3. Configure stricter GitHub environment protection rules for staging
4. Wire deploy-production to the same artifact + promotion model with manual approval gates

## Automated backup workflow

- Workflow: .github/workflows/daily-backup.yml
- Runs daily and can be triggered manually (workflow_dispatch)
- Executes remote backup script and enforces presence of BACKUP_UPLOAD_COMMAND
- Uploads `staging-backup-evidence` artifact for audit trail

## Automated restore drill workflow

- Workflow: .github/workflows/restore-drill.yml
- Runs monthly and can be triggered manually (workflow_dispatch)
- Executes remote restore drill script and table-count validation
- Uploads `restore-drill-evidence` artifact for release signoff

## Verification scope enforced in CI

- URL must be HTTPS (TLS termination check)
- Header presence checks:
	- Strict-Transport-Security
	- X-Content-Type-Options
	- X-Frame-Options
	- Content-Security-Policy
	- Referrer-Policy
