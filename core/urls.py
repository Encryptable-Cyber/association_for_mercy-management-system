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
]