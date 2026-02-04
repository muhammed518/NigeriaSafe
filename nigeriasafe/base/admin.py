from django.contrib import admin

# Register your models here.
from .models import Patient, SOSAlert, Task, Volunteer
admin.site.register(Patient)
admin.site.register(Volunteer)


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'patient', 'status', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('patient__full_name', 'message')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'urgency', 'location', 'created_by', 'isActive', 'created_at')
    list_filter = ('urgency', 'isActive', 'created_at')
    search_fields = ('title', 'description', 'location')
