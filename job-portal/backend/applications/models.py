from django.db import models
from django.conf import settings
from .utils import send_email_async
from .utils import send_push_notification

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    )

    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')

    is_auto_apply = models.BooleanField(default=False)

    # For manual apply: stores cover letter, expected salary, etc.
    manual_answers = models.JSONField(default=dict, blank=True)

    # Snapshot of applicant's profile at application time (used for auto apply)
    snapshot_resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    snapshot_skills = models.JSONField(default=list, blank=True)
    snapshot_experience = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hr_notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def _str_(self):
        return f"{self.applicant.email} -> {self.job.title}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('application_received', 'New Application Received'),
        ('application_status_update', 'Application Status Updated'),
        ('hr_reply', 'HR Reply'),
        ('job_alert', 'Job Alert'),
    )
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def _str_(self):
        return f"Notification for {self.recipient.email}: {self.title}"
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Send email
            send_email_async(
                subject=self.title,
                message=self.message,
                recipient_list=[self.recipient.email],
            )
            # Send push notification (if Firebase is configured and user has tokens)
            send_push_notification(
                user=self.recipient,
                title=self.title,
                body=self.message[:200],   # truncate if too long
                data={'notification_id': str(self.id), 'type': self.notification_type}
            )
class FCMDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fcm_devices')
    registration_token = models.TextField(unique=True)
    device_type = models.CharField(max_length=20, choices=[('web', 'Web'), ('android', 'Android'), ('ios', 'iOS')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"{self.user.email} - {self.device_type}"