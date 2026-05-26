from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from applications.views import RegisterFCMTokenView


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/profiles/', include('profiles.urls')),
    path('api/', include('posts.urls')),
    path('api/', include('jobs.urls')),
    path('api/applications/', include('applications.urls')),
    path('api/network/', include('network.urls')),
    path('api/messaging/', include('messaging.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/push/register/', RegisterFCMTokenView.as_view(), name='register-fcm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
