from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_dashboard, name='public_dashboard'),
]