from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.public_dashboard, name='public_dashboard'),
    
    # Customer
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('complaint/<str:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    
    # Staff
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/unassigned/', views.unassigned_complaints, name='unassigned_complaints'),
    path('complaint/<str:complaint_id>/update/', views.update_complaint_status, name='update_complaint_status'),
    path('complaint/<str:complaint_id>/assign/', views.assign_complaint, name='assign_complaint'),
]