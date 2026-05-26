
from django.db import IntegrityError, transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import JobApplication, Notification
from .serializers import JobApplicationSerializer, ManualApplySerializer, HRReplySerializer, NotificationSerializer
from jobs.models import Job
from profiles.models import Profile

class ApplyManualView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ManualApplySerializer

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, is_active=True)

        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            return Response({'error': 'You have already applied for this job.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Convert Decimal to float for JSON serialization
        manual_data = serializer.validated_data.copy()
        if 'expected_salary' in manual_data and manual_data['expected_salary'] is not None:
            manual_data['expected_salary'] = float(manual_data['expected_salary'])

        application = JobApplication.objects.create(
            job=job,
            applicant=request.user,
            is_auto_apply=False,
            manual_answers=manual_data,
            status='pending'
        )

        # Snapshot profile (if exists)
        profile = Profile.objects.filter(user=request.user).first()
        if profile:
            application.snapshot_resume = profile.resume
            application.snapshot_skills = profile.skills if hasattr(profile, 'skills') else []
            application.snapshot_experience = profile.experience if hasattr(profile, 'experience') else ''
            application.save()

        Notification.objects.create(
            recipient=job.posted_by,
            sender=request.user,
            notification_type='application_received',
            title='New Job Application',
            message=f"{request.user.email} applied for your job '{job.title}'.",
            related_application=application
        )

        return Response(JobApplicationSerializer(application).data, status=status.HTTP_201_CREATED)

# All other views remain unchanged (ApplyAutoView, MyApplicationsView, etc.)
# Keep them as previously provided

class ApplyAutoView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        if getattr(request.user, 'role', None) != 'seeker':
            return Response(
                {
                    'success': False,
                    'message': 'Only candidates can use automate apply.',
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        job = Job.objects.filter(id=job_id, is_active=True).first()
        if not job:
            return Response(
                {
                    'success': False,
                    'message': 'Auto apply is available only for active internal jobs.',
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            return Response(
                {
                    'success': False,
                    'message': 'You have already applied for this job.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = Profile.objects.filter(user=request.user).first()
        snapshot_resume = profile.resume if profile else None
        snapshot_skills = [
            skill.strip()
            for skill in (profile.skills or '').split(',')
            if skill.strip()
        ] if profile else []
        snapshot_experience = profile.experience if profile and hasattr(profile, 'experience') else ''

        try:
            with transaction.atomic():
                application = JobApplication.objects.create(
                    job=job,
                    applicant=request.user,
                    is_auto_apply=True,
                    manual_answers={},
                    status='pending',
                    snapshot_resume=snapshot_resume,
                    snapshot_skills=snapshot_skills,
                    snapshot_experience=snapshot_experience or ''
                )

                Notification.objects.create(
                    recipient=job.posted_by,
                    sender=request.user,
                    notification_type='application_received',
                    title='Auto Application',
                    message=f"{request.user.email} auto-applied for '{job.title}' using their profile.",
                    related_application=application
                )
        except IntegrityError:
            return Response(
                {
                    'success': False,
                    'message': 'You have already applied for this job.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                'success': True,
                'message': 'Auto application submitted successfully.',
                'application': JobApplicationSerializer(application, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED,
        )

class MyApplicationsView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(applicant=self.request.user)

class HRJobApplicationsView(generics.ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        job = get_object_or_404(Job, id=job_id)
        if job.posted_by != self.request.user:
            return JobApplication.objects.none()
        return JobApplication.objects.filter(job=job)

class HRReplyToApplicationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = HRReplySerializer

    def post(self, request, application_id):
        application = get_object_or_404(JobApplication, id=application_id)
        if application.job.posted_by != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if 'status' in serializer.validated_data:
            application.status = serializer.validated_data['status']
            application.save()

        Notification.objects.create(
            recipient=application.applicant,
            sender=request.user,
            notification_type='hr_reply',
            title='HR Response to your application',
            message=serializer.validated_data['message'],
            related_application=application
        )

        return Response({'message': 'Reply sent successfully.'}, status=status.HTTP_200_OK)

class NotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        unread_only = self.request.query_params.get('unread_only', 'false').lower() == 'true'
        if unread_only:
            queryset = queryset.filter(is_read=False)
        return queryset

class UnreadNotificationsCountView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})

class MarkNotificationReadView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read'})
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import FCMDevice
from .serializers import FCMDeviceSerializer   # we'll create next

class RegisterFCMTokenView(generics.CreateAPIView):
    serializer_class = FCMDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        token = serializer.validated_data['registration_token']
        # Remove existing token if any (or update)
        FCMDevice.objects.update_or_create(
            registration_token=token,
            defaults={
                'user': self.request.user,
                'device_type': serializer.validated_data.get('device_type', 'web'),
                'is_active': True,
            }
        )
