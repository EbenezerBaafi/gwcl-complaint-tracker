from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_dashboard, name='public_dashboard'),
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('complaint/<str:complaint_id>/', views.complaint_detail, name='complaint_detail'),
]