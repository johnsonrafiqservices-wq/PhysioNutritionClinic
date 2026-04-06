from .models import ClinicSettings, EnabledModule


def clinic_settings(request):
    """
    Context processor to make clinic settings available in all templates
    """
    try:
        settings = ClinicSettings.get_settings()
        # Get enabled modules
        enabled_modules = EnabledModule.get_enabled_modules()
        return {
            'clinic_settings': settings,
            'enabled_modules': enabled_modules,
        }
    except Exception:
        # Return default values if settings don't exist yet
        # Include all color fields with their defaults
        return {
            'clinic_settings': {
                'clinic_name': 'Alafia Point Wellness Clinic',
                'logo': None,
                # Primary Colors
                'primary_color': '#1B5E96',
                'primary_dark': '#154a7a',
                'primary_light': '#e6f1fa',
                # Success Colors
                'success_color': '#2E8B57',
                'success_dark': '#236b43',
                'success_light': '#e8f5f0',
                # Accent Colors
                'accent_color': '#00A86B',
                'accent_dark': '#008554',
                'accent_light': '#e6f9f3',
                # Warning Colors
                'warning_color': '#FF8C00',
                'warning_dark': '#e67e00',
                'warning_light': '#fff4e6',
                # Danger Colors
                'danger_color': '#dc2626',
                'danger_dark': '#b91c1c',
                'danger_light': '#fecaca',
                # Info Colors
                'info_color': '#0891b2',
                'info_dark': '#0e7490',
                'info_light': '#cffafe',
                # Secondary Colors
                'secondary_color': '#64748b',
                'secondary_dark': '#475569',
                'secondary_light': '#f1f5f9',
                # Base Colors
                'dark_color': '#1e293b',
                'light_color': '#f8fafc',
                'border_color': '#e2e8f0',
                # Text Colors
                'text_primary': '#1e293b',
                'text_secondary': '#64748b',
                'text_muted': '#94a3b8',
                # Background Colors
                'bg_primary': '#ffffff',
                'bg_secondary': '#f8fafc',
                'bg_tertiary': '#f1f5f9',
                # Chart Colors
                'chart_color_1': '#1B5E96',
                'chart_color_2': '#2E8B57',
                'chart_color_3': '#00A86B',
                'chart_color_4': '#FF8C00',
                'chart_color_5': '#0891b2',
                'chart_color_6': '#dc2626',
            },
            # Default all modules to enabled if DB not ready
            'enabled_modules': ['patients', 'appointments', 'medical_records', 'laboratory', 
                               'pharmacy', 'billing', 'budget', 'staff_management', 'reports'],
        }
