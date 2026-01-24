from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Patient, SOSAlert, Task, Volunteer
from .forms import PatientForm, CustomUserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@login_required(login_url='base:signin')
def volunteer(request):
    is_volunteer = hasattr(request.user, 'volunteer_profile')
    
    if request.method == 'POST':
        location = request.POST.get('location')
        medical_training = request.POST.get('Medical Training')
        skills = request.POST.get('skills')
        notes = request.POST.get('notes')
        consent = request.POST.get('consent')

        if not consent:
            messages.error(request, 'You must consent to volunteer.')
            return redirect('base:volunteer')

        Volunteer.objects.update_or_create(
            user=request.user,
            defaults={
                'location': location,
                'skills': skills,
                'medical_training': True if medical_training else False,
                'notes': notes
            }
        )

        messages.success(request, 'Thank you for volunteering! You can now access tasks.')
        return redirect('base:volunteer_tasks')

    return render(request, 'base/volunteer.html', {'is_volunteer': is_volunteer})


def home(request):
    context = {}
    if request.user.is_authenticated:
        try:
            context['patient'] = request.user.patient_profile
        except Patient.DoesNotExist:
            context['patient'] = None
    return render(request, 'base/home.html', context)



@csrf_exempt
def sos_alert(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Expected fields: latitude, longitude, message
        lat = data.get('latitude') or data.get('lat')
        lon = data.get('longitude') or data.get('lon') or data.get('lng')
        message = data.get('message')

        if lat is None or lon is None:
            return JsonResponse({'status': 'error', 'message': 'Missing coordinates'}, status=400)

        patient = None
        if request.user.is_authenticated:
            try:
                patient = request.user.patient_profile
            except Patient.DoesNotExist:
                pass

        try:
            alert = SOSAlert.objects.create(
                patient=patient,
                latitude=lat,
                longitude=lon,
                message=message,
            )
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        return JsonResponse({'status': 'success', 'message': 'Alert received', 'id': alert.id})
    return JsonResponse({'status': 'error'}, status=400)


@staff_member_required
def sos_monitor(request):
    # Staff-only monitoring page showing recent SOS alerts
    alerts = SOSAlert.objects.all()[:200]
    return render(request, 'base/sos_monitor.html', {'alerts': alerts})


def about(request):
    return render(request, 'base/about.html')


def contact(request):
    return render(request, 'base/contact.html')


def resources(request):
    return render(request, 'base/resources.html')


def fire_safety(request):
    return render(request, 'base/fire-safety.html')


def first_aid(request):
    return render(request, 'base/first-Aid.html')


def flooding_safety(request):
    return render(request, 'base/flooding-safety.html')


def landslides_safety(request):
    return render(request, 'base/landslides-safety.html')


def power_outage(request):
    return render(request, 'base/power-outage.html')

def emergency_numbers(request):
    return render(request, 'base/emergency-numbers.html')


def extreme_heat(request):
    return render(request, 'base/extreme-heat.html')


def water_safety(request):
    return render(request, 'base/water-safety.html')


def signin_view(request):
    # Show info if redirected from login_required
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if user exists by email
        user_obj = User.objects.filter(email=email).first()
        if user_obj is None:
            messages.error(request, 'User does not exist. Please sign up.')
            return redirect('base:signin')

        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Signed in successfully.')
            return redirect('base:home')
        else:
            messages.error(request, 'Incorrect email or password.')
        return redirect('base:signin')
    else:
        # GET
        if request.GET.get('next'):
            messages.info(request, 'Please sign in to access that page.')
        return render(request, 'base/signin.html', {'next': request.GET.get('next', '')})


def registerform_view(request):
    if request.method == 'POST':
        # Use email as username since we removed the username field
        data = request.POST.copy()
        data['username'] = data.get('email')
        form = CustomUserCreationForm(data)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created and signed in.')
            # mark new user so they are prompted to complete medical profile
            request.session['new_user'] = True
            return redirect('base:medical_id')
        else:
            for field, errors in form.errors.items():
                for e in errors:
                    messages.error(request, f"{field}: {e}")
            return redirect('base:registerform')
    else:
        form = CustomUserCreationForm()
    return render(request, 'base/registerform.html', {'form': form})


def signout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('base:home')


@login_required(login_url='base:signin')
def medical_id(request):
    # If user already has a profile, load it; otherwise allow creation
    try:
        patient = request.user.patient_profile
    except Patient.DoesNotExist:
        patient = None

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            p = form.save(commit=False)
            p.user = request.user
            p.full_name = request.user.get_full_name()
            p.save()
            # clear new_user flag if present
            if request.session.get('new_user'):
                del request.session['new_user']
            messages.success(request, 'Medical profile saved.')
            return redirect('base:medical_id')
        else:
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PatientForm(instance=patient)

    is_new = bool(request.session.get('new_user', False))
    return render(request, 'base/medical-ID.html', {'form': form, 'is_new': is_new})



@login_required(login_url='base:signin')
def volunteer_tasks(request):
    # Restrict access to volunteers and staff
    if not hasattr(request.user, 'volunteer_profile') and not request.user.is_staff:
        messages.error(request, 'Please sign up as a volunteer to view tasks.')
        return redirect('base:volunteer')

    # Fetch all active tasks, newest first
    tasks = Task.objects.filter(is_active=True).order_by('-created_atat')
    context = {'tasks': tasks}
    return render(request, 'base/volunteer_tasks.html', context)

@login_required(login_url='base:signin')
def create_task(request):
    # Restrict access to staff members only
    if not request.user.is_staff:
        messages.error(request, "Access denied. Only staff can create tasks.")
        return redirect('base:home')

    if request.method == 'POST':
        title = request.POST.get('title')
        location = request.POST.get('location')
        urgency = request.POST.get('urgency')
        description = request.POST.get('description')
        
        # Create the new task
        Task.objects.create(
            title=title,
            location=location,
            urgency=urgency,
            description=description,
            created_by=request.user
        )
        messages.success(request, "Task created successfully!")
        return redirect('base:volunteer_tasks')
        
    return render(request, 'base/admin_create_task.html')


# ===================== ADMIN DASHBOARD VIEWS =====================

@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard view"""
    # Get statistics
    total_sos_alerts = SOSAlert.objects.count()
    pending_alerts = SOSAlert.objects.filter(status=SOSAlert.STATUS_PENDING).count()
    active_tasks = Task.objects.filter(isActive=True).count()
    
    context = {
        'total_sos_alerts': total_sos_alerts,
        'pending_alerts': pending_alerts,
        'active_tasks': active_tasks,
    }
    return render(request, 'base/admin_dashboard.html', context)


@staff_member_required
def sos_alerts_list(request):
    """Display all SOS alerts with search functionality by MRN"""
    search_query = request.GET.get('search', '').strip()
    
    if search_query:
        # Search by Medical Record Number
        alerts = SOSAlert.objects.filter(
            patient__medical_record_number__icontains=search_query
        ).select_related('patient').order_by('-created_at')
    else:
        # Show all alerts, newest first
        alerts = SOSAlert.objects.select_related('patient').order_by('-created_at')
    
    # Get status filter if provided
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    
    context = {
        'alerts': alerts,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': SOSAlert.STATUS_CHOICES,
    }
    return render(request, 'base/admin_sos_alerts.html', context)


@staff_member_required
def sos_alert_detail(request, alert_id):
    """Display detailed view of a single SOS alert"""
    alert = SOSAlert.objects.select_related('patient').get(id=alert_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in SOSAlert.STATUS_CHOICES]:
            alert.status = new_status
            alert.save()
            messages.success(request, f'Alert status updated to {new_status}.')
            return redirect('base:sos_alerts_list')
    
    context = {
        'alert': alert,
        'status_choices': SOSAlert.STATUS_CHOICES,
    }
    return render(request, 'base/admin_sos_alert_detail.html', context)


@staff_member_required
def tasks_management(request):
    """Display all tasks with filtering options"""
    # Get all active tasks
    tasks = Task.objects.select_related('created_by').order_by('-created_at')
    
    # Filter by urgency if provided
    urgency_filter = request.GET.get('urgency', '').strip()
    if urgency_filter:
        tasks = tasks.filter(urgency=urgency_filter)
    
    # Filter by active status
    active_only = request.GET.get('active_only', 'true').lower() == 'true'
    if active_only:
        tasks = tasks.filter(isActive=True)
    
    context = {
        'tasks': tasks,
        'urgency_filter': urgency_filter,
        'active_only': active_only,
        'urgency_choices': Task.URGENCY_CHOICES,
    }
    return render(request, 'base/admin_tasks_management.html', context)


@staff_member_required
def create_admin_task(request):
    """Create a new task from admin panel"""
    volunteers = Volunteer.objects.select_related('user').all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        location = request.POST.get('location')
        urgency = request.POST.get('urgency')
        description = request.POST.get('description')
        assigned_volunteer_id = request.POST.get('assigned_volunteer')
        
        if not all([title, location, urgency, description]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('base:create_admin_task')
        
        task = Task.objects.create(
            title=title,
            location=location,
            urgency=urgency,
            description=description,
            created_by=request.user,
        )
        
        messages.success(request, f'Task "{title}" created successfully!')
        return redirect('base:task_detail', task_id=task.id)
    
    context = {
        'volunteers': volunteers,
        'urgency_choices': Task.URGENCY_CHOICES,
    }
    return render(request, 'base/admin_create_task_form.html', context)


@staff_member_required
def task_detail(request, task_id):
    """View and edit a single task"""
    task = Task.objects.select_related('created_by').get(id=task_id)
    volunteers = Volunteer.objects.select_related('user').all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update':
            task.title = request.POST.get('title', task.title)
            task.location = request.POST.get('location', task.location)
            task.urgency = request.POST.get('urgency', task.urgency)
            task.description = request.POST.get('description', task.description)
            task.save()
            messages.success(request, 'Task updated successfully!')
            
        elif action == 'delete':
            task.delete()
            messages.success(request, 'Task deleted successfully!')
            return redirect('base:tasks_management')
        
        elif action == 'toggle_status':
            task.isActive = not task.isActive
            task.save()
            status_text = 'activated' if task.isActive else 'deactivated'
            messages.success(request, f'Task {status_text} successfully!')
    
    context = {
        'task': task,
        'volunteers': volunteers,
        'urgency_choices': Task.URGENCY_CHOICES,
    }
    return render(request, 'base/admin_task_detail.html', context)


@staff_member_required
def edit_task(request, task_id):
    """Edit a task (alternative view)"""
    task = Task.objects.get(id=task_id)
    
    if request.method == 'POST':
        task.title = request.POST.get('title', task.title)
        task.location = request.POST.get('location', task.location)
        task.urgency = request.POST.get('urgency', task.urgency)
        task.description = request.POST.get('description', task.description)
        task.save()
        messages.success(request, 'Task updated successfully!')
        return redirect('base:task_detail', task_id=task.id)
    
    context = {
        'task': task,
        'urgency_choices': Task.URGENCY_CHOICES,
    }
    return render(request, 'base/admin_edit_task.html', context)


@staff_member_required
def delete_task(request, task_id):
    """Delete a task"""
    task = Task.objects.get(id=task_id)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('base:tasks_management')
    
    context = {'task': task}
    return render(request, 'base/admin_delete_task.html', context)
