import json
import logging
import time

logger = logging.getLogger("security")

SENSITIVE_KEYS = {"password", "password2", "old_password", "new_password", "token", "refresh", "access"}


def _scrub(data):
    if not isinstance(data, dict):
        return data
    return {k: ("***" if k.lower() in SENSITIVE_KEYS else v) for k, v in data.items()}


class AuditLogMiddleware:
    """
    Logs every state-changing API request (method, path, user, IP, status,
    latency) for traceability — a core control expected by NIST CSF
    (Detect / Respond) and the CBN Risk-Based Cybersecurity Framework.
    Full structured entries are additionally persisted via
    apps.accounts.models.AuditLog from within the relevant views.
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
            ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "unknown"))
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