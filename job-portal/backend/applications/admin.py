from django.contrib import admin
from .models import JobApplication, Notification

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'applicant', 'is_auto_apply', 'status', 'applied_at')
    list_filter = ('status', 'is_auto_apply', 'job__posted_by')
    search_fields = ('job_title', 'applicant_email')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('recipient__email', 'title')