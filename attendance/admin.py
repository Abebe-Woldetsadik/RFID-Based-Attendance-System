# attendance/admin.py
from django.contrib import admin
from .models import RFIDCard, Attendance, LatestScanStatus

# -----------------------
# RFIDCard Admin
# -----------------------


@admin.register(RFIDCard)
class RFIDCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'uid', 'get_first_name',
                    'get_last_name')  # columns to show
    search_fields = ('uid', 'user__username', 'user__first_name',
                     'user__last_name')  # searchable fields
    list_filter = ('user',)  # filter by user
    ordering = ('user__username',)  # default ordering

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

# -----------------------
# Attendance Admin
# -----------------------


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_first_name', 'get_last_name',
                    'timestamp', 'status')  # show columns
    search_fields = ('user__username', 'user__first_name',
                     'user__last_name', 'status')  # searchable
    # filter by timestamp, status, or user
    list_filter = ('timestamp', 'status', 'user')
    ordering = ('-timestamp',)  # newest first
    # prevent manual editing of timestamp/status
    readonly_fields = ('timestamp', 'status')

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else "-"
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else "-"
    get_last_name.short_description = 'Last Name'


@admin.register(LatestScanStatus)
class LatestScanStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'message', 'updated_at')
    readonly_fields = ('updated_at',)  # updated automatically
