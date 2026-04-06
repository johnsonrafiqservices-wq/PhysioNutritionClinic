from django import forms
from .models import ClinicSettings


class ClinicSettingsForm(forms.ModelForm):
    class Meta:
        model = ClinicSettings
        fields = ['clinic_name', 'logo', 'address', 'phone', 'email', 'website']
        widgets = {
            'clinic_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter clinic name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter clinic address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter website URL'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class ThemeCustomizationForm(forms.ModelForm):
    """Form for customizing all theme colors with color pickers"""
    
    class Meta:
        model = ClinicSettings
        fields = [
            # Primary Colors
            'primary_color', 'primary_dark', 'primary_light',
            # Success Colors
            'success_color', 'success_dark', 'success_light',
            # Accent Colors
            'accent_color', 'accent_dark', 'accent_light',
            # Warning Colors
            'warning_color', 'warning_dark', 'warning_light',
            # Danger Colors
            'danger_color', 'danger_dark', 'danger_light',
            # Info Colors
            'info_color', 'info_dark', 'info_light',
            # Secondary Colors
            'secondary_color', 'secondary_dark', 'secondary_light',
            # Base Colors
            'dark_color', 'light_color', 'border_color',
            # Text Colors
            'text_primary', 'text_secondary', 'text_muted',
            # Background Colors
            'bg_primary', 'bg_secondary', 'bg_tertiary',
            # Chart Colors
            'chart_color_1', 'chart_color_2', 'chart_color_3',
            'chart_color_4', 'chart_color_5', 'chart_color_6',
        ]
        
        # Create color picker widgets for all color fields
        widgets = {
            # Primary Colors
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'primary_dark': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'primary_light': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # Success Colors
            'success_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'success_dark': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'success_light': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # Accent Colors
            'accent_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'accent_dark': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'accent_light': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # Warning Colors
            'warning_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'warning_dark': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'warning_light': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # Danger Colors
            'danger_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'danger_dark': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'danger_light': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # Info Colors
            'info_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'info_dark': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'info_light': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # Secondary Colors
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_dark': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_light': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # Base Colors
            'dark_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'light_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'border_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # Text Colors
            'text_primary': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'text_secondary': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'text_muted': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # Background Colors
            'bg_primary': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'bg_secondary': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'bg_tertiary': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            # Chart Colors
            'chart_color_1': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'chart_color_2': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'chart_color_3': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'chart_color_4': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'chart_color_5': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'chart_color_6': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }
