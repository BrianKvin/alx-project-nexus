from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.db.models import Avg, Count # For aggregation
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Company, CompanyMember, Review
from .serializers import CompanySerializer, CompanyMemberSerializer, ReviewSerializer
from .permissions import IsCompanyAdminOrOwner, IsOwnerOfReview
from apps.accounts.permissions import IsRecruiter # Assuming IsRecruiter permission exists
from core.pagination import CustomPageNumberPagination # Assuming this exists

class CompanyViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Company instances.
    - List & Retrieve: Accessible by anyone.
    - Create: Only by authenticated recruiters.
    - Update & Delete: Only by company admin/owner.
    """
    queryset = Company.objects.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).all()
    serializer_class = CompanySerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['industry', 'size', 'is_verified']
    search_fields = ['name', 'description', 'headquarters', 'industry']
    ordering_fields = ['name', 'created_at', 'average_rating', 'review_count']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsRecruiter] # Only recruiters can create companies
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsCompanyAdminOrOwner] # Only company admins/owners
        else: # list, retrieve
            self.permission_classes = [AllowAny]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        When a company is created by a recruiter, automatically make that recruiter
        an 'owner' of the company.
        """
        company = serializer.save(is_verified=False) # Companies start as unverified
        CompanyMember.objects.create(
            user=self.request.user,
            company=company,
            role='owner',
            is_active=True
        )

class CompanyMemberViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Company Members.
    - List & Retrieve: Only by authenticated company members (for their own company) or admins.
    - Create, Update, Delete: Only by company owner/admin roles.
    """
    queryset = CompanyMember.objects.all().select_related('user__profile', 'company')
    serializer_class = CompanyMemberSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'user', 'role', 'is_active'] # Filter members by company, user, role

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsCompanyAdminOrOwner] # Only owners/admins can manage members
        elif self.action in ['list', 'retrieve']:
            # Allow authenticated users to list their own company memberships,
            # or admins to list all.
            self.permission_classes = [IsAuthenticated, IsAdminUser | IsCompanyAdminOrOwner]
        else:
            self.permission_classes = [IsAdminUser] # Fallback for safety
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Restrict queryset to company members of the requesting user's companies,
        unless the user is an admin.
        """
        if self.request.user.is_superuser:
            return super().get_queryset()
        
        # Filter for members of companies the user is associated with (as owner/admin/hiring_manager/recruiter)
        associated_company_ids = CompanyMember.objects.filter(user=self.request.user).values_list('company_id', flat=True)
        return super().get_queryset().filter(company__id__in=list(associated_company_ids))


class ReviewViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Company Reviews.
    - List & Retrieve: Accessible by anyone (for all approved reviews).
    - Create: Only by authenticated job seekers.
    - Update & Delete: Only by the reviewer or admin.
    - Approve/Disapprove: Only by admin.
    """
    queryset = Review.objects.filter(is_approved=True).select_related('reviewer__profile', 'company')
    serializer_class = ReviewSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['company', 'reviewer', 'rating', 'is_approved']
    ordering_fields = ['created_at', 'rating']

    def get_queryset(self):
        """
        Admin users can see all reviews (approved or not).
        Non-admin users only see approved reviews.
        """
        if self.request.user.is_superuser:
            return Review.objects.all().select_related('reviewer__profile', 'company')
        return super().get_queryset()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            # Only authenticated job seekers can create reviews
            self.permission_classes = [IsAuthenticated, ~IsRecruiter] # ~IsRecruiter means NOT a recruiter
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsOwnerOfReview | IsAdminUser] # Owner or Admin
        elif self.action in ['approve', 'disapprove']:
            self.permission_classes = [IsAdminUser] # Only Admin for approval
        else: # list, retrieve
            self.permission_classes = [AllowAny] # Anyone can view approved reviews
        return [permission() for permission in self.permission_classes]
    
    def perform_create(self, serializer):
        """
        Sets the reviewer to the authenticated user.
        """
        # Prevent user from reviewing the same company multiple times
        if Review.objects.filter(company=serializer.validated_data['company'], reviewer=self.request.user).exists():
            raise serializers.ValidationError(
                {"detail": "You have already reviewed this company."}
            )
        serializer.save(reviewer=self.request.user, is_approved=False) # Reviews need approval by default

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """
        Admin action to approve a review.
        """
        review = self.get_object()
        review.is_approved = True
        review.save(update_fields=['is_approved'])
        serializer = self.get_serializer(review)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def disapprove(self, request, pk=None):
        """
        Admin action to disapprove a review.
        """
        review = self.get_object()
        review.is_approved = False
        review.save(update_fields=['is_approved'])
        serializer = self.get_serializer(review)
        return Response(serializer.data)


