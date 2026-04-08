from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def admin_dashboard(request):
    """Redirect to the main admin index (jet dashboard)"""
    return redirect('/admin/')
