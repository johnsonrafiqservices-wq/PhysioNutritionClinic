from django.urls import path
from . import views

app_name = 'clinic_settings'

urlpatterns = [
    path('', views.clinic_settings_view, name='settings'),
    path('theme/', views.theme_customization_view, name='theme_customization'),
    path('modules/', views.modules_management_view, name='modules'),
    path('modules/toggle/', views.toggle_module_ajax, name='toggle_module'),
    path('database/', views.database_management_view, name='database'),
    path('database/export/', views.database_export_view, name='database_export'),
    path('database/import/', views.database_import_view, name='database_import'),
]
