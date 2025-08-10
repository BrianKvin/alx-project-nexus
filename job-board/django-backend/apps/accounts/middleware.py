from ratelimit.decorators import ratelimit
from django.http import JsonResponse
from functools import wraps

def rate_limit(key='user_or_ip', rate='5/m', method='ALL'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Apply rate limiting
            @ratelimit(key=key, rate=rate, method=method)
            def limited_view(request, *args, **kwargs):
                return view_func(request, *args, **kwargs)
            
            response = limited_view(request, *args, **kwargs)
            
            if getattr(response, 'limited', False):
                return JsonResponse(
                    {'detail': 'Too many requests. Please try again later.'},
                    status=429
                )
            
            return response
        return _wrapped_view
    return decorator
