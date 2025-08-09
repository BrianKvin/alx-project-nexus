from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class for consistent page size and response format.
    """
    page_size = 10 # Default page size
    page_size_query_param = 'page_size' # Allow client to specify page size
    max_page_size = 100 # Maximum page size allowed

    def get_paginated_response(self, data):
        """
        Overrides the default response format to include pagination metadata.
        """
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'page_size': self.page_size, # Include the effective page size
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })