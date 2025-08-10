from django.contrib import admin
from django.urls import path, include
from apps.core.views.health import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('api/accounts/', include('apps.accounts.urls')),
]
