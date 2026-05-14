"""
Additional security headers middleware.
Adds security-related HTTP headers to every response.
"""


class SecurityHeadersMiddleware:
    """
    Adds security headers to all responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self'; "
        )

        # Permissions Policy
        response['Permissions-Policy'] = (
            "camera=(), microphone=(), geolocation=(), "
            "interest-cohort=()"
        )

        # Cache control for sensitive pages
        if request.path.startswith('/admin/') or request.path.startswith('/auth/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'

        return response

import time
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse


def rate_limit(max_requests=10, window=60):
    """
    Rate limiting decorator.
    Limits requests to max_requests per window (in seconds).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')

            cache_key = f'rate_limit_{ip}_{view_func.__name__}'
            requests_count = cache.get(cache_key, 0)

            if requests_count >= max_requests:
                return HttpResponse(
                    'Too many requests. Please try again later.',
                    status=429
                )

            cache.set(cache_key, requests_count + 1, window)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator