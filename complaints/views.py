from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Complaint, StatusUpdate
from .forms import Complaint, ComplaintForm, ComplaintRatingForm, StatusUpdateForm, ComplaintAssignmentForm
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


# Staff Views

@login_required
def staff_dashboard(request):
    """Staff dashboard showing assigned complaints"""
    if not request.user.is_staff_member():
        messages.error(request, 'Only staff members can access this page.')
        return redirect('dashboard')
    
    # Get assigned complaints
    assigned_complaints = Complaint.objects.filter(assigned_to=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', None)
    if status_filter:
        assigned_complaints = assigned_complaints.filter(status=status_filter)
    
    # Statistics
    total_assigned = assigned_complaints.count()
    in_progress = assigned_complaints.filter(status='in_progress').count()
    resolved = assigned_complaints.filter(status='resolved').count()
    pending = assigned_complaints.filter(status='submitted').count()
    
    # Get unassigned complaints (for staff to pick up)
    unassigned_complaints = Complaint.objects.filter(assigned_to__isnull=True, status='submitted').order_by('-created_at')[:5]
    
    context = {
        'assigned_complaints': assigned_complaints,
        'unassigned_complaints': unassigned_complaints,
        'total_assigned': total_assigned,
        'in_progress': in_progress,
        'resolved': resolved,
        'pending': pending,
        'status_filter': status_filter,
    }
    
    return render(request, 'complaints/staff_dashboard.html', context)


@login_required
def update_complaint_status(request, complaint_id):
    """Staff can update complaint status"""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    
    # Check permissions
    if not request.user.is_staff_member() and not request.user.is_manager():
        messages.error(request, 'You do not have permission to update this complaint.')
        return redirect('complaint_detail', complaint_id=complaint_id)
    
    # Staff can only update their assigned complaints
    if request.user.is_staff_member() and complaint.assigned_to != request.user:
        messages.error(request, 'You can only update complaints assigned to you.')
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            status_update = form.save(commit=False)
            status_update.complaint = complaint
            status_update.updated_by = request.user
            status_update.old_status = complaint.status
            status_update.save()
            
            # Update complaint status
            complaint.status = status_update.new_status
            complaint.save()
            
            messages.success(request, 'Complaint status updated successfully!')
            return redirect('complaint_detail', complaint_id=complaint_id)
    else:
        form = StatusUpdateForm()
    
    context = {
        'complaint': complaint,
        'form': form,
    }
    
    return render(request, 'complaints/update_status.html', context)


@login_required
def assign_complaint(request, complaint_id):
    """Assign or reassign a complaint to staff"""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    
    # Only managers and staff can assign
    if not request.user.is_manager() and not request.user.is_staff_member():
        messages.error(request, 'You do not have permission to assign complaints.')
        return redirect('complaint_detail', complaint_id=complaint_id)
    
    # Staff can self-assign unassigned complaints
    if request.user.is_staff_member() and complaint.assigned_to is not None and complaint.assigned_to != request.user:
        messages.error(request, 'This complaint is already assigned to someone else.')
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        # Quick self-assign for staff
        if 'self_assign' in request.POST and request.user.is_staff_member():
            complaint.assigned_to = request.user
            complaint.status = 'in_progress'
            complaint.save()
            
            # Create status update
            StatusUpdate.objects.create(
                complaint=complaint,
                updated_by=request.user,
                old_status='submitted',
                new_status='in_progress',
                notes=f'Complaint assigned to {request.user.username}'
            )
            
            messages.success(request, 'Complaint assigned to you successfully!')
            return redirect('complaint_detail', complaint_id=complaint_id)
        
        # Full assignment form (for managers)
        form = ComplaintAssignmentForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, 'Complaint assignment updated!')
            return redirect('complaint_detail', complaint_id=complaint_id)
    else:
        form = ComplaintAssignmentForm(instance=complaint)
    
    context = {
        'complaint': complaint,
        'form': form,
    }
    
    return render(request, 'complaints/assign_complaint.html', context)


@login_required
def unassigned_complaints(request):
    """View all unassigned complaints"""
    if not request.user.is_staff_member() and not request.user.is_manager():
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    complaints = Complaint.objects.filter(assigned_to__isnull=True, status='submitted').order_by('-created_at')
    
    context = {
        'complaints': complaints,
    }
    
    return render(request, 'complaints/unassigned_complaints.html', context)