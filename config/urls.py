"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Language switching
    path('i18n/', include('django.conf.urls.i18n')),

    # Django Admin
    path('admin/', admin.site.urls),

    # Authentication (Django built-in)
    path('auth/', include('django.contrib.auth.urls')),

    # Dashboard (home page)
    path('', include('core.urls')),

    # App URLs
    path('beneficiaries/', include('beneficiaries.urls')),
    path('programs/', include('programs.urls')),
    path('donations/', include('donations.urls')),
    path('', include('users.urls')),  # Public membership at root level
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)