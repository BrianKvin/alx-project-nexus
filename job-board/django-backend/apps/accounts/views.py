from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .models import CustomUser, Profile
from .serializers import CustomUserSerializer, ProfileSerializer, UserRegistrationSerializer
from .permissions import IsOwnerOfProfileOrReadOnly

# Core Pagination from your project's `core` directory
from core.pagination import CustomPageNumberPagination # Assuming you create this in core/pagination.py

class CustomUserViewSet(
    mixins.RetrieveModelMixin, # Allow GET (retrieve) for a single user
    mixins.ListModelMixin,     # Allow GET (list) for multiple users
    mixins.UpdateModelMixin,   # Allow PUT/PATCH (update) for a user
    mixins.DestroyModelMixin,  # Allow DELETE (destroy) for a user
    viewsets.GenericViewSet      # Base class for custom actions
):
    """
    A ViewSet for viewing and editing CustomUser instances.
    Only admin users can list all users or view other users' details.
    Users can only update and delete their own accounts.
    """
    queryset = CustomUser.objects.all().select_related('profile') # Eager load profile
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create': # Registration is handled by a separate action below
            self.permission_classes = [AllowAny]
        elif self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # For detail views, ensure it's owner or admin
            self.permission_classes = [IsAuthenticated, IsOwnerOfProfileOrReadOnly | IsAdminUser]
        else: # For list view and any other actions
            self.permission_classes = [IsAdminUser] # Only admins can list all users
        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Endpoint for user registration. Creates a new CustomUser and Profile.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # You might want to return JWT token here after successful registration
        return Response(
            CustomUserSerializer(user, context={'request': request}).data, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Endpoint for authenticated users to view or update their own profile.
        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
        else: # PUT or PATCH
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)

class ProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """
    A ViewSet for viewing and editing Profile instances.
    Users can only view/edit their own profile.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfProfileOrReadOnly]
    lookup_field = 'user__id' # Allow lookup by the associated user's UUID

    def get_object(self):
        """
        Allows retrieving the profile based on the authenticated user's ID
        when accessing /profiles/me/. For other profile IDs, it uses the standard lookup.
        """
        if self.action == 'me':
            return self.request.user.profile
        return super().get_object()

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Retrieve or update the authenticated user's profile.
        """
        profile = request.user.profile
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
        else: # PUT or PATCH
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)