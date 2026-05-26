from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'posted_by', 'is_active', 'created_at')
    list_filter = ('is_active', 'job_type', 'posted_by')
    search_fields = ('title', 'company')
from .models import SavedJob

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'job', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user_email', 'job_title')
    