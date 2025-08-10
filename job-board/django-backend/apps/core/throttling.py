from rest_framework.throttling import UserRateThrottle
from django.core.cache import cache

class JobSearchThrottle(UserRateThrottle):
    scope = 'job_search'
    rate = '100/hour'  # Prevent scraping

class ApplicationThrottle(UserRateThrottle):
    scope = 'applications'
    rate = '10/day'  # Prevent spam applications

class CustomRateThrottle(UserRateThrottle):
    def allow_request(self, request, view):
        # Custom logic based on user tier, IP location, etc.
        user_tier = getattr(request.user, 'subscription_tier', 'free')
        if user_tier == 'premium':
            return True
        return super().allow_request(request, view)
