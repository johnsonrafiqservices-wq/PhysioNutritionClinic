"""
Pagination utility functions for consistent pagination across all list views
"""
from django.core.paginator import Paginator, Page


class FakePaginator:
    """Fake paginator for 'all' option"""
    def __init__(self, count):
        self.count = count
        self.num_pages = 1


class FakePage:
    """Fake page object for 'all' option"""
    def __init__(self, object_list, count):
        self.object_list = object_list
        self.paginator = FakePaginator(count)
        self.number = 1
        
    def __iter__(self):
        return iter(self.object_list)
    
    def __len__(self):
        return len(self.object_list)
    
    @property
    def start_index(self):
        return 1 if len(self.object_list) > 0 else 0
    
    @property
    def end_index(self):
        return len(self.object_list)
    
    def has_other_pages(self):
        return False
    
    def has_previous(self):
        return False
    
    def has_next(self):
        return False


def paginate_queryset(request, queryset, default_page_size=25):
    """
    Paginate a queryset with dynamic page size support.
    
    Args:
        request: Django request object
        queryset: QuerySet to paginate
        default_page_size: Default number of items per page (default: 25)
    
    Returns:
        dict: Contains page_obj, page_size, query_string, and items
    """
    # Get page size from request
    page_size = request.GET.get('page_size', str(default_page_size))
    
    # Handle "all" option
    if page_size == 'all':
        # Create a fake page object for template compatibility
        count = queryset.count()
        fake_page = FakePage(list(queryset), count)
        return {
            'page_obj': fake_page,
            'items': queryset,
            'page_size': 'all',
            'query_string': build_query_string(request),
        }
    
    # Convert to integer with fallback
    try:
        page_size = int(page_size)
    except ValueError:
        page_size = default_page_size
    
    # Create paginator
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return {
        'page_obj': page_obj,
        'items': page_obj,
        'page_size': page_size,
        'query_string': build_query_string(request),
    }


def build_query_string(request):
    """
    Build query string from request GET parameters, excluding 'page'.
    
    Args:
        request: Django request object
    
    Returns:
        str: Query string with leading '&' or empty string
    """
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    return '&' + query_params.urlencode() if query_params else ''
