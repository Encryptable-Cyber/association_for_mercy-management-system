from django.urls import path
from . import views

app_name = 'beneficiaries'

urlpatterns = [
    path('', views.beneficiary_list, name='list'),
    path('new/', views.beneficiary_create, name='create'),
    path('report/', views.beneficiary_report, name='report'),
    path('<int:pk>/', views.beneficiary_detail, name='detail'),
    path('<int:pk>/edit/', views.beneficiary_edit, name='edit'),
    path('<int:beneficiary_pk>/case/new/', views.case_create, name='case_create'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
    path('cases/<int:case_pk>/intervention/', views.intervention_create, name='intervention_create'),
]