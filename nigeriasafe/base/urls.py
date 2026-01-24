from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('resources/', views.resources, name='resources'),
    path('resources/fire-safety/', views.fire_safety, name='fire_safety'),
    path('resources/first-aid/', views.first_aid, name='first_aid'),
    path('resources/flooding-safety/', views.flooding_safety, name='flooding_safety'),
    path('resources/landslides-safety/', views.landslides_safety, name='landslides_safety'),
    path('resources/power-outage/', views.power_outage, name='power_outage'),
    path('resources/extreme-heat/', views.extreme_heat, name='extreme_heat'),
    path('resources/water-safety/', views.water_safety, name='water_safety'),
    path('emergency-numbers/', views.emergency_numbers, name='emergency_numbers'),
    path('signin/', views.signin_view, name='signin'),
    path('registerform/', views.registerform_view, name='registerform'),
    path('logout/', views.signout_view, name='logout'),
    path('medical-id/', views.medical_id, name='medical_id'),
    path('volunteer/', views.volunteer, name='volunteer'),
    path('signout/', views.signout_view, name='signout'),
    path('api/sos-alert/', views.sos_alert, name='sos_alert'),
    path('sos-monitor/', views.sos_monitor, name='sos_monitor'),
    path('volunteer/tasks/', views.volunteer_tasks, name='volunteer_tasks'),
    path('staff/create-task/', views.create_task, name='create_task'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/sos/<int:alert_id>/update/', views.update_sos_status, name='update_sos_status'),
    path('dashboard/task/<int:task_id>/update/', views.update_task, name='update_task'),
    path('dashboard/task/<int:task_id>/toggle/', views.toggle_task_active, name='toggle_task_active'),
    path('task/<int:task_id>/status/', views.update_volunteer_task_status, name='update_volunteer_task_status'),
]
 