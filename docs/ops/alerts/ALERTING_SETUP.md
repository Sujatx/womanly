# Alerting Setup

This document defines alert rules and integration points for MVP operations.

## Rules file

- docs/ops/alerts/prometheus-alert-rules.yml

## Covered alert conditions

1. Error-rate spike
- Alert: WomanlyHighErrorRate
- Condition: 5xx ratio > 5% for 10m

2. Payment failure spike
- Alert: WomanlyPaymentFailureSpike
- Condition: payment endpoint 4xx/5xx ratio > 10% for 10m

3. DB health issue
- Alert: WomanlyDbUnavailable
- Condition: readiness/health probe failing for 3m

4. Backup failure/missing run
- Alert: WomanlyBackupMissing24h
- Condition: no successful backup in 24h

5. Restore drill staleness
- Alert: WomanlyRestoreDrillMissing30d
- Condition: no successful restore drill in 30d

## Notes

- `womanly_last_backup_timestamp_seconds` and `womanly_last_restore_drill_timestamp_seconds` should be exported by your backup/restore workflows via your metrics pipeline (pushgateway/exporter/agent).
- `probe_success{job="womanly-health"}` assumes blackbox probing for staging/prod readiness endpoints.
- Route Alertmanager notifications to Slack/PagerDuty/email based on severity labels.
