from django.urls import path
from . import views

app_name = 'programs'

urlpatterns = [
    path('', views.program_list, name='list'),
    path('new/', views.program_create, name='create'),
    path('report/', views.program_report, name='report'),
    path('<int:pk>/', views.program_detail, name='detail'),
    path('<int:pk>/edit/', views.program_edit, name='edit'),
]