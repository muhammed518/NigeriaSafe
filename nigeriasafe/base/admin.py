from django.contrib import admin

# Register your models here.
from .models import Patient
admin.site.register(Patient)
from .models import SOSAlert, Task, Volunteer


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'patient', 'status', 'createdAt')
	list_filter = ('status', 'createdAt')
	search_fields = ('patient__full_name', 'message')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'urgency', 'location', 'createdBy', 'isActive', 'createdAt')
    list_filter = ('urgency', 'isActive', 'createdAt')
    search_fields = ('title', 'description', 'location')

admin.site.register(Volunteer)