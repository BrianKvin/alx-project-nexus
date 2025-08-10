from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, ProfileViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Password reset endpoints
    path('auth/password/reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    
    # Main API endpoints
    path('', include(router.urls)),
]