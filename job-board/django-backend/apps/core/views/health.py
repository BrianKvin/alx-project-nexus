from django.http import JsonResponse
from django.views import View

class HealthCheckView(View):
    """
    Health check endpoint for Docker health checks
    """
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "healthy"}, status=200)
