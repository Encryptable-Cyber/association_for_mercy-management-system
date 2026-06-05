from django.urls import path
from django.http import HttpResponse
from . import views

app_name = 'core'

def health_check(request):
    """Lightweight health check for load balancers and monitoring."""
    return HttpResponse('ok', content_type='text/plain')

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('health/', health_check, name='health_check'),
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/new/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/edit/', views.activity_edit, name='activity_edit'),
    path('activities/<int:pk>/toggle/', views.activity_toggle, name='activity_toggle'),
]