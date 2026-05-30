from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Public
    path('membership/apply/', views.membership_apply, name='membership_apply'),
    path('membership/thanks/', views.membership_thanks, name='membership_thanks'),
    path('membership/signup/<uuid:token>/', views.membership_signup, name='membership_signup'),

    # Admin review
    path('memberships/', views.membership_list, name='membership_list'),
    path('memberships/<int:pk>/', views.membership_review, name='membership_review'),

    # Super Admin - User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:pk>/change-role/', views.user_change_role, name='user_change_role'),
    path('memberships/report/', views.membership_report, name='membership_report'),
    path('users/report/', views.user_report, name='user_report'),
    path('users/<int:pk>/reset-password/', views.user_reset_password, name='user_reset_password'),
    path('membership/<int:pk>/upload/', views.membership_upload_document, name='membership_upload_document'),
    path('otp/verify/', views.otp_verify, name='otp_verify'),
    path('password-reset/otp/', views.otp_verify_password_reset, name='otp_verify_password_reset'),
    path('audit-log/', views.audit_log, name='audit_log'),
]