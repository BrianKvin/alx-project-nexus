from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Category, Location
from .serializers import CategorySerializer, LocationSerializer
from core.pagination import CustomPageNumberPagination # Assuming this exists

class CategoryViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Category instances.
    - List & Retrieve: Accessible by anyone.
    - Create, Update & Delete: Only by admin users.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else: # create, update, partial_update, destroy
            self.permission_classes = [IsAdminUser]
        return [permission() for permission in self.permission_classes]

class LocationViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Location instances.
    - List & Retrieve: Accessible by anyone.
    - Create, Update & Delete: Only by admin users.
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_remote', 'country', 'city'] # Simple filters
    search_fields = ['city', 'state_province', 'country']
    ordering_fields = ['country', 'city', 'created_at']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else: # create, update, partial_update, destroy
            self.permission_classes = [IsAdminUser]
        return [permission() for permission in self.permission_classes]

