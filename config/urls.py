"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views
from users.views import OTPPasswordResetConfirmView

urlpatterns = [
    # Language switching
    path('i18n/', include('django.conf.urls.i18n')),

    # Django Admin
    path('admin/', admin.site.urls),

    # Authentication (custom password reset with OTP)
    path('auth/', include([
        path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
        path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        path('reset/<uidb64>/<token>/', OTPPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
        path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    ])),

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