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
        # Clinic Quick Actions
        self.children.append(modules.LinkList(
            _('Quick Actions'),
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
                    'url': '/admin/laboratory/labtestrequest/add/',
                    'external': False,
                },
                {
                    'title': _('Go to Dashboard'),
                    'url': '/dashboard/',
                    'external': False,
                },
            ],
            column=0,
            order=0
        ))

        # Recent Activity
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            10,
            column=0,
            order=1
        ))

        # Patient Management
        self.children.append(modules.ModelList(
            _('Patient Management'),
            models=('patients.*',),
            column=1,
            order=0
        ))

        # Appointments & Billing
        self.children.append(modules.ModelList(
            _('Appointments & Billing'),
            models=('appointments.*', 'billing.*'),
            column=1,
            order=1
        ))

        # Pharmacy
        self.children.append(modules.ModelList(
            _('Pharmacy'),
            models=('pharmacy.*',),
            column=2,
            order=0
        ))

        # Medical Records & Lab
        self.children.append(modules.ModelList(
            _('Laboratory & Medical Records'),
            models=('laboratory.*', 'medical_records.*'),
            column=2,
            order=1
        ))

        # Staff & System
        self.children.append(modules.ModelList(
            _('Staff & System'),
            models=('staff_management.*', 'accounts.*', 'clinic_settings.*', 'budget.*'),
            column=0,
            order=2
        ))


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for clinic system
    """
    def init_with_context(self, context):
        self.children.append(modules.ModelList(
            title=_('Application Models'),
            models=('*',),
            column=0,
            order=0
        ))
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            10,
            column=1,
            order=0
        ))
