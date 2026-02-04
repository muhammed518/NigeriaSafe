from django.db import models
from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import Authorization
from base.models import Patient, SOSAlert

class PatientResource(ModelResource):
    class Meta:
        queryset = Patient.objects.all()
        resource_name = 'patient'
        authorization = Authorization()
        excludes = ['created_at', 'updated_at']

class SOSAlertResource(ModelResource):
    patient = fields.ForeignKey(PatientResource, 'patient', null=True, blank=True, full=True)

    class Meta:
        queryset = SOSAlert.objects.all()
        resource_name = 'sos_alert'
        authorization = Authorization()
        always_return_data = True
        allowed_methods = ['get', 'post']