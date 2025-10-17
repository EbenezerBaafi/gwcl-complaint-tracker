from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Complaint(models.Model):
    """Model for customer complaints"""
    
    CATEGORY_CHOICES = (
        ('leak', 'Water Leak'),
        ('no_water', 'No Water Supply'),
        ('billing', 'Billing Issue'),
        ('water_quality', 'Water Quality'),
        ('meter_issue', 'Meter Issue'),
        ('pressure', 'Low Water Pressure'),
        ('other', 'Other'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    # Auto-generated complaint ID
    complaint_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Relationships
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='complaints'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_complaints',
        limit_choices_to={'role': 'staff'}
    )
    
    # Complaint Details
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Location
    address = models.TextField()
    gps_coordinates = models.CharField(max_length=50, blank=True, null=True)
    
    # File Upload
    image = models.ImageField(upload_to='complaints/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Customer Satisfaction
    customer_rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    customer_feedback = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
    
    def __str__(self):
        return f"{self.complaint_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Generate complaint ID if not exists
        if not self.complaint_id:
            year = timezone.now().year
            count = Complaint.objects.filter(created_at__year=year).count() + 1
            self.complaint_id = f"GWCL-{year}-{count:05d}"
        
        # Set resolved_at when status changes to resolved
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def response_time(self):
        """Calculate response time in hours"""
        if self.resolved_at:
            delta = self.resolved_at - self.created_at
            return round(delta.total_seconds() / 3600, 2)  # hours
        return None
    
    @property
    def is_overdue(self):
        """Check if complaint is overdue (more than 48 hours)"""
        if self.status in ['resolved', 'closed']:
            return False
        delta = timezone.now() - self.created_at
        return delta.total_seconds() > (48 * 3600)


class StatusUpdate(models.Model):
    """Model for tracking complaint status changes and updates"""
    
    complaint = models.ForeignKey(
        Complaint, 
        on_delete=models.CASCADE, 
        related_name='status_updates'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    notes = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Status Update'
        verbose_name_plural = 'Status Updates'
    
    def __str__(self):
        return f"{self.complaint.complaint_id} - {self.new_status} at {self.created_at}"