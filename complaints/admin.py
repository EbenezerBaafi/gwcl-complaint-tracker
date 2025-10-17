from django.contrib import admin
from .models import Complaint, StatusUpdate

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['complaint_id', 'title', 'customer', 'category', 'priority', 'status', 'created_at']
    list_filter = ['status', 'category', 'priority', 'created_at']
    search_fields = ['complaint_id', 'title', 'description', 'customer__username']
    readonly_fields = ['complaint_id', 'created_at', 'updated_at', 'resolved_at']
    
    fieldsets = (
        ('Complaint Information', {
            'fields': ('complaint_id', 'customer', 'title', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'priority', 'status')
        }),
        ('Location', {
            'fields': ('address', 'gps_coordinates', 'image')
        }),
        ('Assignment', {
            'fields': ('assigned_to',)
        }),
        ('Feedback', {
            'fields': ('customer_rating', 'customer_feedback')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at')
        }),
    )

@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'old_status', 'new_status', 'updated_by', 'created_at']
    list_filter = ['new_status', 'created_at']
    search_fields = ['complaint__complaint_id', 'notes']
    readonly_fields = ['created_at']