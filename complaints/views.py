from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Complaint, StatusUpdate
from .forms import Complaint, ComplaintForm, ComplaintRatingForm
from django.contrib import messages

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


# Customer Views

@login_required
def submit_complaint(request):
    """Customer can submit a new complaint"""
    if not request.user.is_customer():
        messages.error(request, 'Only customers can submit complaints.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.customer = request.user
            complaint.save()
            
            messages.success(request, f'Complaint submitted successfully! Your complaint ID is {complaint.complaint_id}')
            return redirect('my_complaints')
    else:
        form = ComplaintForm()
    
    return render(request, 'complaints/submit_complaint.html', {'form': form})


@login_required
def my_complaints(request):
    """Customer can view their own complaints"""
    if not request.user.is_customer():
        messages.error(request, 'Only customers can view this page.')
        return redirect('dashboard')
    
    complaints = Complaint.objects.filter(customer=request.user).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', None)
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    context = {
        'complaints': complaints,
        'status_filter': status_filter,
    }
    
    return render(request, 'complaints/my_complaints.html', context)


@login_required
def complaint_detail(request, complaint_id):
    """View detailed complaint information with status history"""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    
    # Check permissions
    if request.user.is_customer() and complaint.customer != request.user:
        messages.error(request, 'You can only view your own complaints.')
        return redirect('my_complaints')
    
    # Get status updates
    status_updates = complaint.status_updates.all()
    
    # Handle rating form (only for resolved complaints by the customer)
    rating_form = None
    if request.user == complaint.customer and complaint.status in ['resolved', 'closed'] and not complaint.customer_rating:
        if request.method == 'POST':
            rating_form = ComplaintRatingForm(request.POST, instance=complaint)
            if rating_form.is_valid():
                rating_form.save()
                messages.success(request, 'Thank you for your feedback!')
                return redirect('complaint_detail', complaint_id=complaint_id)
        else:
            rating_form = ComplaintRatingForm(instance=complaint)
    
    context = {
        'complaint': complaint,
        'status_updates': status_updates,
        'rating_form': rating_form,
    }
    
    return render(request, 'complaints/complaint_detail.html', context)