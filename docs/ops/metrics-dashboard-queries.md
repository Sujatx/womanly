# Metrics Dashboard Queries

This file defines baseline Prometheus queries for the MVP observability dashboard.

## Scrape target

- Endpoint: /metrics
- Suggested scrape interval: 15s

## Panels

1. API request rate (RPS)
- sum(rate(womanly_http_requests_total[5m]))

2. API error rate (5xx)
- sum(rate(womanly_http_requests_total{status=~"5.."}[5m])) / sum(rate(womanly_http_requests_total[5m]))

3. API p95 latency
- histogram_quantile(0.95, sum(rate(womanly_http_request_duration_seconds_bucket[5m])) by (le))

4. API p99 latency
- histogram_quantile(0.99, sum(rate(womanly_http_request_duration_seconds_bucket[5m])) by (le))

5. Payment failure rate (verify/create-order endpoints)
- sum(rate(womanly_http_requests_total{path=~"/api/v1/payments/(create-order|verify)",status=~"4..|5.."}[5m])) / sum(rate(womanly_http_requests_total{path=~"/api/v1/payments/(create-order|verify)"}[5m]))

6. Order throughput
- sum(rate(womanly_http_requests_total{path="/api/v1/payments/create-order",status=~"2.."}[5m]))

7. In-flight requests
- womanly_http_inflight_requests

8. Unhandled server errors
- sum(increase(womanly_http_server_errors_total[15m]))

## Alert recommendations

- High error rate: > 5% for 10m
- p95 latency: > 1.0s for 10m
- Payment failure spike: > 10% for 10m
- Server error spike: > 20 in 15m
