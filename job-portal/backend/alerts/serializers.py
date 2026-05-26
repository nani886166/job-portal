from rest_framework import serializers
from .models import JobAlertPreference

class JobAlertPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAlertPreference
        fields = ['id', 'user', 'receive_job_alerts', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']