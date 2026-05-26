# applications/utils.py
import threading
from django.core.mail import send_mail
from django.conf import settings
import threading
from django.core.mail import send_mail
from django.conf import settings

def send_email_async(subject, message, recipient_list, html_message=None):
    """Send email in a background thread to avoid blocking the request."""
    def _send():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email failed to {recipient_list}: {e}")
    thread = threading.Thread(target=_send)
    thread.start()
 # push notifications (Firebase)
try:
    from firebase_admin import messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

def send_push_notification(user, title, body, data=None):
    if not FIREBASE_AVAILABLE:
        return
    from .models import FCMDevice   # will define next
    devices = FCMDevice.objects.filter(user=user, is_active=True)
    if not devices:
        return
    tokens = [dev.registration_token for dev in devices]
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        tokens=tokens,
        data=data or {},
    )
    try:
        response = messaging.send_multicast(message)
        # Optionally delete failed tokens
        if response.failure_count > 0:
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    # Remove invalid token
                    FCMDevice.objects.filter(registration_token=tokens[idx]).delete()
    except Exception as e:
        print(f"Push failed: {e}")

def send_email_async(subject, message, recipient_list, html_message=None):
    """Send email in a background thread to avoid blocking the request."""
    def _send():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email failed to {recipient_list}: {e}")
    thread = threading.Thread(target=_send)
    thread.start()
