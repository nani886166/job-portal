from django.urls import path
from .views import (
    ApplyManualView, ApplyAutoView, MyApplicationsView,
    HRJobApplicationsView, HRReplyToApplicationView,
    NotificationsView, UnreadNotificationsCountView, MarkNotificationReadView
)

urlpatterns = [
    # Seeker endpoints
    path('apply/manual/<int:job_id>/', ApplyManualView.as_view(), name='apply-manual'),
    path('apply/auto/<int:job_id>/', ApplyAutoView.as_view(), name='apply-auto'),
    path('my/', MyApplicationsView.as_view(), name='my-applications'),

    # HR endpoints
    path('hr/jobs/<int:job_id>/applications/', HRJobApplicationsView.as_view(), name='hr-job-applications'),
    path('hr/reply/<int:application_id>/', HRReplyToApplicationView.as_view(), name='hr-reply'),

    # Notifications
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('notifications/unread-count/', UnreadNotificationsCountView.as_view(), name='unread-count'),
    path('notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark-read'),
]