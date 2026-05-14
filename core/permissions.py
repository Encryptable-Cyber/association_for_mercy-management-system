from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """
    Decorator for views that require Admin role.
    Raises PermissionDenied (403) instead of redirecting to login,
    preventing information leakage about protected URLs.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")
        if not request.user.is_admin:
            raise PermissionDenied("Admin privileges required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def staff_required(view_func):
    """
    Decorator for views that require at least Staff role.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")
        if not (request.user.is_admin or request.user.is_staff_user):
            raise PermissionDenied("Staff privileges required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view