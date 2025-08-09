from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend # For filtering
from rest_framework import filters # For search

from .models import Job, JobApplication
from .serializers import JobSerializer, JobApplicationSerializer, JobApplicationCreateSerializer
from .permissions import IsJobPosterOrReadOnly, IsCompanyAdminOrJobPoster, IsApplicantOrRecruiter
from apps.accounts.permissions import IsRecruiter, IsJobSeeker
from apps.jobs.filters import JobFilter # Assuming you will create this in jobs/filters.py
from core.pagination import CustomPageNumberPagination # Assuming you create this in core/pagination.py
from apps.companies.models import CompanyMember # To validate recruiter company affiliation

class JobViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Job instances.
    - List & Retrieve: Accessible by anyone (read-only).
    - Create: Only by authenticated recruiters.
    - Update & Delete: Only by the job poster OR a company admin/hiring manager.
    """
    queryset = Job.objects.all().select_related('company', 'category', 'location', 'posted_by')
    serializer_class = JobSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter # Link to your custom filterset
    search_fields = ['title', 'description', 'company__name', 'location__city', 'location__country', 'category__name']
    ordering_fields = ['created_at', 'application_deadline', 'salary_min', 'views_count']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated, IsRecruiter] # Only recruiters can post jobs
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only job poster or company admin/hiring manager can modify/delete
            self.permission_classes = [IsAuthenticated, IsCompanyAdminOrJobPoster]
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny] # Anyone can view jobs
        elif self.action == 'apply':
            self.permission_classes = [IsAuthenticated, IsJobSeeker] # Only job seekers can apply
        else:
            self.permission_classes = [IsAuthenticated] # Default for other actions

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        Automatically sets the `posted_by` field to the authenticated user
        and increments `views_count` on retrieval.
        """
        # Ensure the creating user is associated with a company if required (business logic)
        # For simplicity, we assume IsRecruiter permission handles that a profile exists
        # You might add more checks here, e.g., if user is a member of the company_id provided
        
        # Verify the recruiter belongs to the company they are trying to post a job for
        company_id = self.request.data.get('company_id')
        if company_id:
            try:
                CompanyMember.objects.get(
                    user=self.request.user, 
                    company_id=company_id,
                    role__in=['owner', 'admin', 'hiring_manager', 'recruiter']
                )
            except CompanyMember.DoesNotExist:
                raise serializers.ValidationError(
                    {"company_id": "You are not authorized to post jobs for this company."}
                )

        serializer.save(posted_by=self.request.user, source='manual')

    def retrieve(self, request, *args, **kwargs):
        """
        Increments the views_count for a job when it's retrieved.
        """
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsJobSeeker])
    def apply(self, request, pk=None):
        """
        Endpoint for job seekers to apply to a specific job.
        """
        job = self.get_object()
        applicant = request.user

        # Prevent duplicate applications
        if JobApplication.objects.filter(job=job, applicant=applicant).exists():
            return Response(
                {"detail": "You have already applied for this job."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use a separate serializer for application creation that expects fewer fields
        serializer = JobApplicationCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Automatically set job and applicant fields
        application = serializer.save(job=job, applicant=applicant)

        # You might trigger a Celery task here to send an email notification
        # from apps.notifications.tasks import send_application_received_notification
        # send_application_received_notification.delay(application.id)

        return Response(
            JobApplicationSerializer(application).data, 
            status=status.HTTP_201_CREATED
        )

class JobApplicationViewSet(viewsets.ReadOnlyModelViewSet, mixins.UpdateModelMixin):
    """
    A ViewSet for viewing and updating JobApplication instances.
    - List: Only by recruiters (filtering by company/posted_by).
    - Retrieve: By applicant (their own) or recruiter (for their company's jobs).
    - Update: Only by recruiters (to change status).
    """
    queryset = JobApplication.objects.all().select_related('job__company', 'applicant__profile')
    serializer_class = JobApplicationSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # filterset_class = JobApplicationFilter # You might create a filter for applications
    ordering_fields = ['applied_at', 'status']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list']:
            self.permission_classes = [IsAuthenticated, IsRecruiter] # Only recruiters can list applications
        elif self.action in ['retrieve', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsApplicantOrRecruiter]
        else: # Default for any other actions (e.g., destroy, not explicitly allowed here)
            self.permission_classes = [IsAdminUser] # Fallback to admin permission

        return [permission() for permission in self.permission_classes]
    
    def get_queryset(self):
        """
        Optionally restricts the returned applications to a given user (job seeker)
        or applications for jobs posted by their company (recruiter).
        """
        user = self.request.user
        if user.is_authenticated:
            if hasattr(user, 'profile') and user.profile.user_type == 'job_seeker':
                return self.queryset.filter(applicant=user)
            elif hasattr(user, 'profile') and user.profile.user_type == 'recruiter':
                # Filter applications for jobs posted by companies the recruiter is associated with
                company_ids = CompanyMember.objects.filter(user=user).values_list('company__id', flat=True)
                return self.queryset.filter(job__company_id__in=list(company_ids))
        return JobApplication.objects.none() # No applications for unauthenticated or non-specific users

    def perform_update(self, serializer):
        """
        Only recruiters can update the status of an application.
        """
        # Ensure the user has permission to update this application (handled by IsApplicantOrRecruiter)
        # You might add specific logic here to restrict status changes based on role
        if self.request.user.profile.user_type == 'recruiter':
            serializer.save()
        else:
            # If a job seeker tries to update, they can only withdraw
            if self.request.user == serializer.instance.applicant:
                if 'status' in serializer.validated_data and serializer.validated_data['status'] == 'withdrawn':
                    serializer.save(status='withdrawn')
                else:
                    raise serializers.ValidationError({"detail": "Job seekers can only withdraw their applications."})
            else:
                raise serializers.ValidationError({"detail": "You do not have permission to update this application."})

