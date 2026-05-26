
from rest_framework import serializers
from .models import JobApplication, Notification
from jobs.serializers import JobSerializer
from .models import FCMDevice

class JobApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    applicant_email = serializers.EmailField(source='applicant.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_details = JobSerializer(source='job', read_only=True)

    class Meta:
        model = JobApplication
        fields = '__all__'   # not { '_all' }
        read_only_fields = ['id', 'applicant', 'applied_at', 'updated_at', 'snapshot_resume', 'snapshot_skills', 'snapshot_experience']

    def get_applicant_name(self, obj):
        return f"{obj.applicant.first_name} {obj.applicant.last_name}".strip() or obj.applicant.email

class ManualApplySerializer(serializers.Serializer):
    cover_letter = serializers.CharField(required=True)
    # Use DecimalField for validation, but we will convert to float later
    expected_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    additional_info = serializers.JSONField(required=False, default=dict)

class HRReplySerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    status = serializers.ChoiceField(choices=JobApplication.STATUS_CHOICES, required=False)

class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'sender', 'sender_name', 'notification_type', 'title', 'message', 'related_application', 'is_read', 'created_at']
        read_only_fields = ['id', 'recipient', 'created_at']

    def get_sender_name(self, obj):
        if obj.sender:
            return f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.email
        return None

class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['registration_token', 'device_type', 'is_active']