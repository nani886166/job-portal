from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .models import Job, SavedJob
from .serializers import JobSerializer, SavedJobSerializer


class IsHROrReadOnly(permissions.BasePermission):
    message = 'Only the HR user who posted this job can change it.'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'hr'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.posted_by


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsHROrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'company', 'description', 'location']
    ordering_fields = ['created_at', 'salary_min', 'salary_max']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Job.objects.all().select_related('posted_by')
        if self.action in ['list', 'retrieve', 'save']:
            queryset = queryset.filter(is_active=True)
        return queryset

    def success_response(self, message, data=None, status_code=status.HTTP_200_OK, **extra):
        payload = {
            'success': True,
            'message': message,
        }
        if data is not None:
            payload.update(data)
            payload['data'] = next(iter(data.values())) if len(data) == 1 else data
        payload.update(extra)
        return Response(payload, status=status_code)

    def perform_create(self, serializer):
        if getattr(self.request.user, 'role', None) != 'hr':
            raise PermissionDenied('Only HR can post jobs.')
        serializer.save(posted_by=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated = self.get_paginated_response(serializer.data).data
            return self.success_response(
                'Jobs fetched successfully.',
                {'jobs': paginated.get('results', [])},
                count=paginated.get('count'),
                next=paginated.get('next'),
                previous=paginated.get('previous'),
            )

        serializer = self.get_serializer(queryset, many=True)
        return self.success_response('Jobs fetched successfully.', {'jobs': serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self.success_response(
            'Job created successfully.',
            {'job': serializer.data},
            status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return self.success_response('Job fetched successfully.', {'job': serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.success_response('Job updated successfully.', {'job': serializer.data})

    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.get_object())
        return self.success_response('Job deleted successfully.')

    @action(detail=False, methods=['get'], url_path='my-jobs', permission_classes=[permissions.IsAuthenticated])
    def my_jobs(self, request):
        if getattr(request.user, 'role', None) != 'hr':
            return Response(
                {'success': False, 'message': 'Only HR can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        jobs = Job.objects.filter(posted_by=request.user).select_related('posted_by').order_by('-created_at')
        serializer = self.get_serializer(jobs, many=True)
        return self.success_response('Your posted jobs fetched successfully.', {'jobs': serializer.data})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def save(self, request, pk=None):
        job = self.get_object()
        saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
        if not created:
            saved.delete()
            return Response(
                {'success': True, 'saved': False, 'message': 'Job unsaved'},
                status=status.HTTP_200_OK,
            )
        return Response(
            {'success': True, 'saved': True, 'message': 'Job saved'},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def saved(self, request):
        saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job', 'user')
        serializer = SavedJobSerializer(saved_jobs, many=True)
        return Response(
            {
                'success': True,
                'message': 'Saved jobs fetched successfully.',
                'saved_jobs': serializer.data,
                'data': serializer.data,
            }
        )
