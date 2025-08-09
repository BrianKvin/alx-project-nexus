from django.contrib import admin
from django.urls import path
from apps.core.views.health import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]
