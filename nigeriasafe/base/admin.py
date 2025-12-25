from django.contrib import admin

# Register your models here.
from .models import Patient
admin.site.register(Patient)
from .models import SOSAlert, Task, Volunteer


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'patient', 'status', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('patient__full_name', 'message')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'urgency', 'location', 'created_by', 'is_active', 'created_at')
    list_filter = ('urgency', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'location')

admin.site.register(Volunteer)