import json
import logging
import time

logger = logging.getLogger("security")


def get_client_ip(request):
    """Get the real client IP, handling proxies."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
        return ip
    return request.META.get("REMOTE_ADDR", "unknown")


class AuditLogMiddleware:
    """
    Logs every state-changing API request for traceability.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        if request.path.startswith("/api/") and request.method in ("POST", "PUT", "PATCH", "DELETE"):
            duration_ms = round((time.time() - start) * 1000, 1)
            user = getattr(request, "user", None)
            username = getattr(user, "email", "anonymous") if user and user.is_authenticated else "anonymous"
            ip = get_client_ip(request)
            logger.info(json.dumps({
                "event": "api_request",
                "method": request.method,
                "path": request.path,
                "user": username,
                "ip": ip,
                "status": response.status_code,
                "duration_ms": duration_ms,
            }))
        return response


class SecurityHeadersMiddleware:
    """Adds defense-in-depth HTTP security headers to every response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response["Content-Security-Policy"] = "default-src 'self'"
        return response