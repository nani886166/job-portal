from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import JobAlertPreference
from .serializers import JobAlertPreferenceSerializer

class AlertPreferenceView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/alerts/preference/ - manage email/notification preferences"""
    serializer_class = JobAlertPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pref, created = JobAlertPreference.objects.get_or_create(user=self.request.user)
        return pref