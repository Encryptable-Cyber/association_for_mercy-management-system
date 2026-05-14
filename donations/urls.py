from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    # Internal
    path('', views.donation_list, name='list'),
    path('new/', views.donation_create, name='create'),

    # Public
    path('intent/', views.donation_intent_create, name='intent_create'),
    path('intent/thanks/', views.donation_intent_thanks, name='intent_thanks'),

    # Admin review
    path('intents/review/', views.donation_intent_list, name='intent_list'),
    path('intents/review/<int:pk>/', views.donation_intent_review, name='intent_review'),
    
    path('report/', views.donation_report, name='report'),
]