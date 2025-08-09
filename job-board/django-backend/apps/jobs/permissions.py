from rest_framework import permissions
from apps.accounts.permissions import IsRecruiter
from apps.companies.models import CompanyMember

class IsJobPosterOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the user who posted the job to edit/delete it.
    Read-only access is allowed for any authenticated user.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request.
        if request.method in permissions.SAFE_METHODS:
            return True # Any user can view jobs

        # Write permissions are only allowed to the user who posted the job.
        return obj.posted_by == request.user

class IsCompanyAdminOrJobPoster(permissions.BasePermission):
    """
    Custom permission to allow only the user who posted the job, OR
    an admin/owner of the company that owns the job, to edit/delete it.
    Requires IsRecruiter to be true for the user's profile.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the requesting user is the job poster
        if obj.posted_by == request.user:
            return True

        # Check if the requesting user is a recruiter and an admin/owner of the company
        if IsRecruiter().has_permission(request, view):
            try:
                company_member = CompanyMember.objects.get(user=request.user, company=obj.company)
                return company_member.role in ['owner', 'admin', 'hiring_manager']
            except CompanyMember.DoesNotExist:
                return False
        return False


class IsApplicantOrRecruiter(permissions.BasePermission):
    """
    Custom permission to allow a job seeker to view their own application,
    or a recruiter associated with the job's company to view any application for that job.
    """
    def has_object_permission(self, request, view, obj):
        # Applicant can view their own application
        if obj.applicant == request.user:
            return True

        # Recruiter associated with the company that posted the job can view the application
        if IsRecruiter().has_permission(request, view):
            try:
                # Check if the recruiter is associated with the company of the job
                return CompanyMember.objects.filter(
                    user=request.user, 
                    company=obj.job.company,
                    role__in=['owner', 'admin', 'hiring_manager', 'recruiter'] # Any recruiter role
                ).exists()
            except CompanyMember.DoesNotExist:
                return False
        return False

