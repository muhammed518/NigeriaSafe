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
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST


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
    tasks = Task.objects.filter(isActive=True).order_by('-created_at')
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
            created_by=request.user,
            isActive=True
        )
        messages.success(request, "Task created successfully!")
        return redirect('base:admin_dashboard')
        
    return render(request, 'base/admin_create_task.html')


@staff_member_required
def update_sos_status(request, alert_id):
    """Update SOS alert status"""
    if request.method == 'POST':
        try:
            alert = SOSAlert.objects.get(id=alert_id)
            status = request.POST.get('status')
            
            if status in dict(SOSAlert.STATUS_CHOICES):
                alert.status = status
                alert.save()
                messages.success(request, f"SOS Alert #{alert.id} status updated to {status}")
            else:
                messages.error(request, "Invalid status provided")
        except SOSAlert.DoesNotExist:
            messages.error(request, "SOS Alert not found")
    
    return redirect(request.META.get('HTTP_REFERER', 'base:admin_dashboard'))


@staff_member_required
def toggle_task_active(request, task_id):
    """Toggle task active/inactive status"""
    try:
        task = Task.objects.get(id=task_id)
        task.isActive = not task.isActive
        task.save()
        status_text = "activated" if task.isActive else "deactivated"
        messages.success(request, f"Task '{task.title}' has been {status_text}")
    except Task.DoesNotExist:
        messages.error(request, "Task not found")
    
    return redirect(request.META.get('HTTP_REFERER', 'base:admin_dashboard'))


@staff_member_required
def update_task(request, task_id):
    """Update or deactivate a task"""
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id)
            
            task.title = request.POST.get('title', task.title)
            task.location = request.POST.get('location', task.location)
            task.urgency = request.POST.get('urgency', task.urgency)
            task.description = request.POST.get('description', task.description)
            task.isActive = request.POST.get('isActive') == 'on'
            task.save()
            messages.success(request, "Task updated successfully!")
            
        except Task.DoesNotExist:
            messages.error(request, "Task not found")
    
    return redirect(request.META.get('HTTP_REFERER', 'base:admin_dashboard'))


@login_required(login_url='base:signin')
def update_volunteer_task_status(request, task_id):
    """Allow volunteers to update task status"""
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id)
            new_status = request.POST.get('status')
            
            if new_status in dict(Task.STATUS_CHOICES):
                task.status = new_status
                task.save()
                messages.success(request, f"Task '{task.title}' status updated to {task.get_status_display()}")
            else:
                messages.error(request, "Invalid status provided")
        except Task.DoesNotExist:
            messages.error(request, "Task not found")
    
    return redirect(request.META.get('HTTP_REFERER', 'base:volunteer_tasks'))

def admin_dashboard(request):
    # Restrict access to staff members only
    if not request.user.is_staff:
        messages.error(request, "Access denied. Only staff can view the admin dashboard.")
        return redirect('base:home')

    # Get filter parameters
    tab = request.GET.get('tab', 'overview')
    search_mrn = request.GET.get('search_mrn', '')
    sos_status = request.GET.get('sos_status', '')
    task_urgency = request.GET.get('task_urgency', '')

    # Overview stats
    total_patients = Patient.objects.count()
    total_volunteers = Volunteer.objects.count()
    total_sos_alerts = SOSAlert.objects.count()
    total_tasks = Task.objects.count()
    pending_alerts = SOSAlert.objects.filter(status=SOSAlert.STATUS_PENDING).count()

    # Search patients by MRN
    patient_details = None
    if search_mrn:
        try:
            patient_details = Patient.objects.get(medical_record_number__iexact=search_mrn)
        except Patient.DoesNotExist:
            messages.warning(request, f"No patient found with MRN: {search_mrn}")

    # Get SOS Alerts with optional filtering
    sos_alerts = SOSAlert.objects.all().order_by('-created_at')
    if sos_status:
        sos_alerts = sos_alerts.filter(status=sos_status)

    # Get Tasks with optional filtering
    tasks = Task.objects.all().order_by('-created_at')
    if task_urgency:
        tasks = tasks.filter(urgency=task_urgency)

    # Get recent data for dashboard
    recent_alerts = SOSAlert.objects.all().order_by('-created_at')[:10]
    recent_tasks = Task.objects.all().order_by('-created_at')[:10]
    recent_patients = Patient.objects.all().order_by('-created_at')[:10]
    volunteers = Volunteer.objects.all().order_by('-created_at')


    context = {
        'tab': tab,
        'total_patients': total_patients,
        'total_volunteers': total_volunteers,
        'total_sos_alerts': total_sos_alerts,
        'pending_alerts': pending_alerts,
        'total_tasks': total_tasks,
        'sos_alerts': sos_alerts,
        'tasks': tasks,
        'recent_alerts': recent_alerts,
        'recent_tasks': recent_tasks,
        'recent_patients': recent_patients,
        'volunteers': volunteers,
        'patient_details': patient_details,
        'search_mrn': search_mrn,
        'sos_status': sos_status,
        'task_urgency': task_urgency,
    }

    return render(request, 'base/admin_dashboard.html', context)

@require_POST
def send_sos_email(request):
    try:
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return JsonResponse({'message': 'Coordinates missing'}, status=400)

        # Construct Google Maps link
        maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
        
        subject = "SOS: Emergency Location Alert"
        message = (
            f"Emergency Alert!\n\n"
            f"Coordinates received:\n"
            f"Latitude: {latitude}\n"
            f"Longitude: {longitude}\n\n"
            f"View on Google Maps: {maps_link}"
        )
        
        # Replace with the actual emergency contact email you want to alert
        recipient_list = ['emergency_contact@example.com']
        
        if request.user.is_authenticated:
            try:
                if request.user.patient_profile.emergency_contact_email:
                    recipient_list = [request.user.patient_profile.emergency_contact_email]
            except Patient.DoesNotExist:
                pass
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
        )
        
        return JsonResponse({'message': 'SOS Email sent successfully!'})
    except Exception as e:
        return JsonResponse({'message': f'Error sending email: {str(e)}'}, status=500)