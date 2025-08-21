from rest_framework import serializers
from .models import AttendanceLog


class AttendanceLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceLog
        fields = ["id", "uid", "status", "timestamp", "username"]

    def get_username(self, obj):
        return obj.rfid_user.user.username if obj.rfid_user else "Unknown"
