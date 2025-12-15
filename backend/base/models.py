from django.db import models

# Create your models here.
class Patient(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    weight = models.FloatField()
    height = models.FloatField()
    medical_conditions = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    emergency_contact_name = models.CharField(max_length=60)
    emergency_contact_phone = models.CharField(max_length=15)
    emergency_contact_relationship = models.CharField(max_length=30)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # medical_record_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.medical_record_number})" 