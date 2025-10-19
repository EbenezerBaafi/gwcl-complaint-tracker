from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Complaint, StatusUpdate

def public_dashboard(request):
    """Public dashboard showing overall statistics"""
    
    # Total complaints
    total_complaints = Complaint.objects.count()
    
    # Status breakdown
    submitted = Complaint.objects.filter(status='submitted').count()
    in_progress = Complaint.objects.filter(status='in_progress').count()
    resolved = Complaint.objects.filter(status='resolved').count()
    closed = Complaint.objects.filter(status='closed').count()
    
    # Calculate average resolution time (in hours)
    resolved_complaints = Complaint.objects.filter(status__in=['resolved', 'closed']).exclude(resolved_at=None)
    avg_resolution_time = None
    if resolved_complaints.exists():
        total_time = sum([c.response_time for c in resolved_complaints if c.response_time])
        avg_resolution_time = round(total_time / resolved_complaints.count(), 2) if resolved_complaints.count() > 0 else 0
    
    # Complaints by category
    complaints_by_category = Complaint.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent complaints (last 5)
    recent_complaints = Complaint.objects.all()[:5]
    
    # Complaints this month
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    complaints_this_month = Complaint.objects.filter(created_at__gte=this_month).count()
    
    # Overdue complaints
    overdue_count = sum(1 for c in Complaint.objects.filter(status__in=['submitted', 'in_progress']) if c.is_overdue)
    
    context = {
        'total_complaints': total_complaints,
        'submitted': submitted,
        'in_progress': in_progress,
        'resolved': resolved,
        'closed': closed,
        'avg_resolution_time': avg_resolution_time,
        'complaints_by_category': complaints_by_category,
        'recent_complaints': recent_complaints,
        'complaints_this_month': complaints_this_month,
        'overdue_count': overdue_count,
    }
    
    return render(request, 'complaints/public_dashboard.html', context)