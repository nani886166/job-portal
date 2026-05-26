# from rest_framework import serializers
# from .models import Job

# class JobSerializer(serializers.ModelSerializer):
#     posted_by_email = serializers.EmailField(source='posted_by.email', read_only=True)
#     days_ago = serializers.SerializerMethodField()

#     class Meta:
#         model = Job
#         fields = '_all_'
#         read_only_fields = ['id', 'posted_by', 'created_at', 'updated_at']

#     def get_days_ago(self, obj):
#         from django.utils import timezone
#         delta = timezone.now() - obj.created_at
#         return delta.
from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    posted_by_email = serializers.EmailField(source='posted_by.email', read_only=True)
    posted_by_name = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    days_ago = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = '__all__'          # <-- must be exactly 'all_' (two underscores on each side)
        # or use a list: fields = ['id', 'title', 'company', ...]
        read_only_fields = ['id', 'posted_by', 'created_at', 'updated_at']

    def get_posted_by_name(self, obj):
        first_name = getattr(obj.posted_by, 'first_name', '') or ''
        last_name = getattr(obj.posted_by, 'last_name', '') or ''
        return f"{first_name} {last_name}".strip() or obj.posted_by.email

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.posted_by_id == request.user.id)

    def get_days_ago(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        return delta.days

from .models import SavedJob

class SavedJobSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)

    class Meta:
        model = SavedJob
        fields = ['id', 'user', 'job', 'job_details', 'saved_at']
        read_only_fields = ['id', 'user', 'saved_at']
