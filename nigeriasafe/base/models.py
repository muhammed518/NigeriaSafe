from django.db import models
from django.conf import settings

from django.contrib.auth.models import User

import uuid

def generate_medical_record_number():
    """Generate a reasonably short, unique medical record number.

    Uses a UUID4 hex substring with an 'MRN' prefix. Collisions are extremely
    unlikely; if you need a strictly sequential or DB-backed MRN, replace this
    with a database sequence or lock-protected counter.
    """ 
    return f"MRN{uuid.uuid4().hex[:4].upper()}"

# Create your models here.
class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='patient_profile'
    )
    full_name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField()
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, null=True, blank=True)
    weight = models.FloatField()
    height = models.FloatField()
    medical_conditions = models.CharField(max_length=255, null=True, blank=True)
    allergies = models.CharField(max_length=255, null=True, blank=True)
    medications = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    emergency_contact_name = models.CharField(max_length=60)
    emergency_contact_phone = models.CharField(max_length=15)
    emergency_contact_email = models.EmailField(null=True, blank=True)
    emergency_contact_relationship = models.CharField(max_length=30)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    medical_record_number = models.CharField(max_length=20, unique=True, default=generate_medical_record_number, editable=False)

    def __str__(self):
        name = self.user.get_full_name() if self.user else "Unknown"
        return f"{name} - MRN: {self.medical_record_number}"


class SOSAlert(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACK = 'acknowledged'
    STATUS_RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACK, 'Acknowledged'),
        (STATUS_RESOLVED, 'Resolved'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sos_alerts'
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    message = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_display = self.patient.full_name if self.patient else 'Anonymous'
        return f"SOS from {user_display} @ {self.created_at:%Y-%m-%d %H:%M}"
    




class Task(models.Model):
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='medium')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Volunteer(models.Model):
    AVAILABLESTATUS_CHOICES = [
        ('Immediate (within 30 mins)', 'Immediate (within 30 mins)'),
        ('Within 1 hour', 'Within 1 hour'),
        ('Scheduled / On-call', 'Scheduled / On-call'),
        ('Weekends', 'Weekends'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile')
    skills = models.TextField(null=True, blank=True)
    medical_training = models.BooleanField(default=False)
    isAvailable = models.CharField(max_length=200, choices=AVAILABLESTATUS_CHOICES, default='Immediate (within 30 mins)')
    location = models.CharField(max_length=200, null=True, blank=True)
    vehicleDetails = models.TextField(null=True, blank=True)
    equipment = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
     
