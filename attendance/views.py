from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.http import HttpResponse
import json
import csv
from .models import RFIDCard, Attendance, LatestScanStatus


@csrf_exempt
def rfid_scan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        uid = data.get('uid')
        now = timezone.now()

        try:
            card = RFIDCard.objects.get(uid=uid)

            # Check last 6 hours
            six_hours_ago = now - timedelta(hours=6)
            recently_scanned = Attendance.objects.filter(
                user=card.user,
                timestamp__gte=six_hours_ago
            ).exists()

            if recently_scanned:
                status_text = f"Card already scanned within 6 hours: {card.user.username}"
                # Update or create LatestScanStatus
                latest_status, created = LatestScanStatus.objects.get_or_create(
                    id=1)
                latest_status.status = "warning"
                latest_status.message = status_text
                latest_status.updated_at = now
                latest_status.save()
                return JsonResponse({'status': 'warning', 'message': status_text})

            # Successful scan
            status_text = f"Scan successful: {card.user.username}"
            Attendance.objects.create(
                user=card.user, status=status_text, timestamp=now)
            latest_status, created = LatestScanStatus.objects.get_or_create(
                id=1)
            latest_status.status = "success"
            latest_status.message = status_text
            latest_status.updated_at = now
            latest_status.save()
            return JsonResponse({'status': 'success', 'message': status_text})

        except RFIDCard.DoesNotExist:
            status_text = f"Unknown card scanned: {uid}"
            Attendance.objects.create(
                user=None, status=status_text, timestamp=now)
            latest_status, created = LatestScanStatus.objects.get_or_create(
                id=1)
            latest_status.status = "error"
            latest_status.message = status_text
            latest_status.updated_at = now
            latest_status.save()
            return JsonResponse({'status': 'error', 'message': status_text})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def attendance_live(request):
    latest_record = Attendance.objects.order_by('-timestamp').first()
    status_message = latest_record.status if latest_record else "Waiting for scan..."
    attendances = Attendance.objects.order_by(
        '-timestamp')[:20]  # last 20 scans
    return render(request, "attendance/live.html", {
        "status_message": status_message,
        "attendances": attendances
    })


def attendance_list(request):
    query = request.GET.get('q', '')
    attendances = Attendance.objects.order_by('-timestamp')  # all records
    if query:
        attendances = attendances.filter(
            Q(status__icontains=query)
        )
    return render(request, "attendance/list.html", {"attendances": attendances})


def latest_scan_status(request):
    latest_record = Attendance.objects.order_by('-timestamp').first()
    if latest_record:
        status_message = latest_record.status
        latest_timestamp = latest_record.timestamp.isoformat()
    else:
        status_message = "Waiting for scan..."
        latest_timestamp = None

    # Return last 20 attendance records for table
    records = Attendance.objects.order_by('-timestamp')[:20]
    data = []
    for r in records:
        data.append({
            "username": r.user.username if r.user else "Unknown",
            "first_name": r.user.first_name if r.user else "-",
            "last_name": r.user.last_name if r.user else "-",
            "timestamp": r.timestamp.strftime("M. j, Y, g:i a"),
            "status": r.status,
        })

    return JsonResponse({
        "status_message": status_message,
        "latest_timestamp": latest_timestamp,
        "records": data
    })


def live_status(request):
    latest_status = LatestScanStatus.objects.order_by(
        '-updated_at').select_related('user').first()

    # Match Attendance with that same user & closest timestamp
    latest_attendance = None
    if latest_status:
        latest_attendance = Attendance.objects.filter(
            user=latest_status.user).order_by('-timestamp').first()

    return render(request, 'attendance/live.html', {
        'latest_status': latest_status,
        'latest_attendance': latest_attendance,
    })


def live_status_json(request):
    now = timezone.now()
    try:
        latest_status = LatestScanStatus.objects.get(id=1)
    except LatestScanStatus.DoesNotExist:
        latest_status = None

    status_message = "Waiting for scan..."
    status_type = "idle"

    if latest_status and latest_status.updated_at >= now - timedelta(seconds=5):
        status_message = latest_status.message
        status_type = latest_status.status  # "warning", "success", "error"

    # Send latest 10 attendance records
    attendances = Attendance.objects.order_by('-timestamp')[:1]
    records = []
    for a in attendances:
        records.append({
            "username": a.user.username if a.user else "Unknown",
            "first_name": a.user.first_name if a.user else "-",
            "last_name": a.user.last_name if a.user else "-",
            "timestamp": timezone.localtime(a.timestamp).strftime("%b. %d, %Y, %I:%M %p").lower(),
            "status": a.status,
        })

    return JsonResponse({
        "status_message": status_message,
        "status_type": status_type,
        "records": records
    })


def attendance_export_csv(request):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="attendance_list.csv"'},
    )

    writer = csv.writer(response)
    # Write CSV header row
    writer.writerow(['Username', 'First Name',
                    'Last Name', 'Timestamp', 'Status'])

    # Query all attendance records
    attendances = Attendance.objects.order_by('-timestamp')

    for a in attendances:
        writer.writerow([
            a.user.username if a.user else "Unknown",
            a.user.first_name if a.user else "-",
            a.user.last_name if a.user else "-",
            timezone.localtime(a.timestamp).strftime("%b. %d, %Y, %I:%M %p"),
            a.status,
        ])

    return response
