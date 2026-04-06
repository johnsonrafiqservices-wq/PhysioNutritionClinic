"""
Custom Django Jet Dashboard for PhysioNutrition Clinic
"""
from django.utils.translation import gettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for clinic system
    """
    columns = 3

    def init_with_context(self, context):
        # Clinic Overview Module
        self.available_children.append(modules.LinkList(
            _('Clinic Quick Actions'),
            layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                {
                    'title': _('Add New Patient'),
                    'url': '/admin/patients/patient/add/',
                    'external': False,
                },
                {
                    'title': _('Schedule Appointment'),
                    'url': '/admin/appointments/appointment/add/',
                    'external': False,
                },
                {
                    'title': _('Create Invoice'),
                    'url': '/admin/billing/invoice/add/',
                    'external': False,
                },
                {
                    'title': _('Lab Test Request'),
                    'url': '/admin/laboratory/testrequest/add/',
                    'external': False,
                },
            ],
            column=0,
            order=0
        ))

        # Recent Activity Module
        self.available_children.append(modules.RecentActions(
            _('Recent Actions'),
            10,
            column=0,
            order=1
        ))

        # Patient Statistics
        self.available_children.append(modules.ModelList(
            _('Patient Management'),
            models=('patients.*',),
            column=1,
            order=0
        ))

        # Appointments & Billing
        self.available_children.append(modules.ModelList(
            _('Appointments & Billing'),
            models=('appointments.*', 'billing.*'),
            column=1,
            order=1
        ))

        # Medical Records & Lab
        self.available_children.append(modules.ModelList(
            _('Medical Records & Laboratory'),
            models=('medical_records.*', 'laboratory.*'),
            column=2,
            order=0
        ))

        # System Management
        self.available_children.append(modules.ModelList(
            _('System Management'),
            models=('accounts.*', 'clinic_settings.*', 'inventory.*'),
            column=2,
            order=1
        ))

        # Feed Module for System Updates
        self.available_children.append(modules.Feed(
            _('System Status'),
            feed_url='',
            limit=5,
            column=0,
            order=2
        ))


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for clinic system
    """
    def init_with_context(self, context):
        self.available_children.append(modules.ModelList(
            title=_('Application models'),
            models=('*',),
            column=0,
            order=0
        ))
        self.available_children.append(modules.RecentActions(
            _('Recent Actions'),
            10,
            column=1,
            order=0
        ))
