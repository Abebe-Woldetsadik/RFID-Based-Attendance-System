# attendance/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class RFIDCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.CharField(max_length=50, unique=True)  # UID as string

    def __str__(self):
        return f"{self.user.username} - {self.uid}"


class Attendance(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100)  # store status text

    def __str__(self):
        return f"{self.user.username} - {self.timestamp} - {self.status}"


class LatestScanStatus(models.Model):
    # Always keep only one object; update on each scan
    # success, warning, error, info
    status = models.CharField(max_length=20, default="info")
    message = models.CharField(max_length=200, default="Waiting for scan...")
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.status}: {self.message}"
