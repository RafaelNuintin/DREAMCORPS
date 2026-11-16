from django.urls import path
from . import views

urlpatterns = [
    path('', views.ranking_dashboard, name='ranking_dashboard'),
    path('api/sessions/', views.submit_session, name='submit_session'),
    path('api/ranking/', views.ranking_api, name='ranking_api'),
]
