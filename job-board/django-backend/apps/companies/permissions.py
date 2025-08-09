from rest_framework import permissions
from .models import CompanyMember

class IsCompanyAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow admin or owner roles of a specific company
    to modify that company's details or manage its members.
    Requires the user to be authenticated and belong to the company.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to company owner/admin/hiring manager
        if not request.user.is_authenticated:
            return False

        if isinstance(obj, Company):
            # Check if user is an owner/admin/hiring manager of this company
            return CompanyMember.objects.filter(
                user=request.user, 
                company=obj, 
                role__in=['owner', 'admin', 'hiring_manager']
            ).exists()
        
        # If the object is a CompanyMember, check if the user is an admin/owner of that member's company
        if isinstance(obj, CompanyMember):
            return CompanyMember.objects.filter(
                user=request.user,
                company=obj.company,
                role__in=['owner', 'admin'] # Only owners/admins can manage members
            ).exists()
        
        return False

class IsOwnerOfReview(permissions.BasePermission):
    """
    Custom permission to only allow the reviewer to edit/delete their own review.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the reviewer.
        return obj.reviewer == request.user

