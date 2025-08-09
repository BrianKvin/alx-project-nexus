from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Notification
from .serializers import NotificationSerializer
from .permissions import IsNotificationRecipientOrAdmin
from core.pagination import CustomPageNumberPagination # Assuming this exists

class NotificationViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    A ViewSet for viewing and managing Notification instances.
    - List & Retrieve: Only by the recipient or admin.
    - Delete: Only by the recipient or admin.
    - Mark as read/unread: Only by the recipient or admin.
    Notifications are created by the system, not directly via API.
    """
    queryset = Notification.objects.all().select_related('recipient__profile', 'actor__profile')
    serializer_class = NotificationSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['read', 'type'] # Filter by read status and type
    ordering_fields = ['created_at', 'read']

    def get_queryset(self):
        """
        Restricts queryset to notifications for the requesting user,
        unless the user is an admin.
        """
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(recipient=self.request.user)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'destroy', 'mark_as_read', 'mark_as_unread']:
            self.permission_classes = [IsAuthenticated, IsNotificationRecipientOrAdmin]
        else:
            self.permission_classes = [IsAdminUser] # Default for any other (e.g., direct create)
        return [permission() for permission in self.permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsNotificationRecipientOrAdmin])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific notification as read.
        """
        notification = self.get_object()
        notification.read = True
        notification.save(update_fields=['read'])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsNotificationRecipientOrAdmin])
    def mark_all_as_read(self, request):
        """
        Mark all unread notifications for the requesting user as read.
        """
        queryset = self.get_queryset().filter(read=False)
        updated_count = queryset.update(read=True)
        return Response({'detail': f'Marked {updated_count} notifications as read.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsNotificationRecipientOrAdmin])
    def mark_as_unread(self, request, pk=None):
        """
        Mark a specific notification as unread.
        """
        notification = self.get_object()
        notification.read = False
        notification.save(update_fields=['read'])
        return Response(self.get_serializer(notification).data)

