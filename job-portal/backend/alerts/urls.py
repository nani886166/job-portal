from django.urls import path
from .views import AlertPreferenceView

urlpatterns = [
    path('preference/', AlertPreferenceView.as_view(), name='alert-preference'),
]