from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    path('hospitals/', views.hospital_list, name='hospital_list'),
    path('hospitals/<int:pk>/', views.hospital_detail, name='hospital_detail'),
]
