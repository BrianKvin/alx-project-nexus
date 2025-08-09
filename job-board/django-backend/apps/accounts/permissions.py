from rest_framework import permissions

class IsOwnerOfProfileOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object (profile) to edit it.
    Read-only access is allowed for any authenticated user.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions are only allowed to the owner of the profile.
        return obj.user == request.user

class IsRecruiter(permissions.BasePermission):
    """
    Custom permission to only allow users with 'recruiter' user_type in their profile.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            # Check if the user has a profile and if their user_type is 'recruiter'
            return hasattr(request.user, 'profile') and request.user.profile.user_type == 'recruiter'
        return False

class IsJobSeeker(permissions.BasePermission):
    """
    Custom permission to only allow users with 'job_seeker' user_type in their profile.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            # Check if the user has a profile and if their user_type is 'job_seeker'
            return hasattr(request.user, 'profile') and request.user.profile.user_type == 'job_seeker'
        return False