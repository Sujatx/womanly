"""Prometheus metrics middleware for HTTP request observability."""

from time import perf_counter

from prometheus_client import Counter, Gauge, Histogram


HTTP_REQUESTS_TOTAL = Counter(
    "womanly_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "womanly_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

HTTP_INFLIGHT_REQUESTS = Gauge(
    "womanly_http_inflight_requests",
    "In-flight HTTP requests",
)

HTTP_SERVER_ERRORS_TOTAL = Counter(
    "womanly_http_server_errors_total",
    "Total unhandled server-side errors",
    ["method", "path"],
)


def _resolve_route_path(request) -> str:
    route = request.scope.get("route")
    if route and getattr(route, "path", None):
        return route.path
    return request.url.path


async def metrics_middleware(request, call_next):
    """Record per-request metrics for Prometheus scraping."""
    method = request.method
    start = perf_counter()
    HTTP_INFLIGHT_REQUESTS.inc()

    status_code = "500"
    path_label = request.url.path

    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        path_label = _resolve_route_path(request)
        return response
    except Exception:
        path_label = _resolve_route_path(request)
        HTTP_SERVER_ERRORS_TOTAL.labels(method=method, path=path_label).inc()
        raise
    finally:
        elapsed = perf_counter() - start
        HTTP_REQUESTS_TOTAL.labels(method=method, path=path_label, status=status_code).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path_label, status=status_code).observe(elapsed)
        HTTP_INFLIGHT_REQUESTS.dec()