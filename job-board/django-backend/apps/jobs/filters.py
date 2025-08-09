import django_filters
from .models import Job

class JobFilter(django_filters.FilterSet):
    """
    FilterSet for the Job model.
    Allows filtering jobs by various criteria.
    """
    title = django_filters.CharFilter(lookup_expr='icontains') # Case-insensitive contains
    job_type = django_filters.ChoiceFilter(choices=Job.JOB_TYPE_CHOICES)
    experience_level = django_filters.ChoiceFilter(choices=Job.EXPERIENCE_LEVEL_CHOICES)
    is_active = django_filters.BooleanFilter()
    
    salary_min_gte = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max_lte = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')

    company_name = django_filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    location_city = django_filters.CharFilter(field_name='location__city', lookup_expr='icontains')
    location_country = django_filters.CharFilter(field_name='location__country', lookup_expr='icontains')
    location_is_remote = django_filters.BooleanFilter(field_name='location__is_remote')

    deadline_before = django_filters.DateTimeFilter(field_name='application_deadline', lookup_expr='lte')
    
    posted_by = django_filters.UUIDFilter(field_name='posted_by__id')


    class Meta:
        model = Job
        fields = [
            'title', 'job_type', 'experience_level', 'is_active', 
            'salary_min_gte', 'salary_max_lte', 
            'company_name', 'category_name', 'location_city', 
            'location_country', 'location_is_remote', 'deadline_before',
            'posted_by'
        ]
