from django import template

register = template.Library()

@register.filter
def count_by_status(queryset, status):
    """Filter queryset by status and return count"""
    return queryset.filter(status=status).count()

@register.filter
def filter_status(queryset, status):
    """Filter queryset by status"""
    return queryset.filter(status=status)
