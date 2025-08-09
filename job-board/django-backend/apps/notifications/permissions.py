from rest_framework import permissions

class IsNotificationRecipientOrAdmin(permissions.BasePermission):
  """
  Custom permission to only allow the recipient of a notification to view/mark as read.
  Admin users can manage all notifications.
  """
  def has_object_permission(self, request, view, obj):
      # Read/Write permissions are only allowed to the recipient or admin.
      if request.user.is_superuser:
          return True
      
      return obj.recipient == request.user