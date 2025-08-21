# attendance/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_live, name='attendance_live'),
    path('list/', views.attendance_list, name='attendance_list'),
    path('api/rfid-scan/', views.rfid_scan, name='rfid_scan'),
    path('api/latest-status/', views.latest_scan_status, name='latest_scan_status'),
    # urls.py
    path('api/live-status/', views.live_status_json, name='live_status_json'),
    path('list/export/csv/', views.attendance_export_csv,
         name='attendance_export_csv'),

]
