from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    # Dashboard
    path('', views.budget_dashboard, name='dashboard'),
    
    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/create/', views.budget_create, name='budget_create'),
    path('budgets/<int:pk>/', views.budget_detail, name='budget_detail'),
    path('budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('budgets/<int:budget_pk>/add-item/', views.budget_item_create, name='budget_item_create'),
    
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/approve/', views.expense_approve, name='expense_approve'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    
    # AJAX Endpoints
    path('ajax/expense/create/', views.expense_create_ajax, name='expense_create_ajax'),
    path('ajax/budget/create/', views.budget_create_ajax, name='budget_create_ajax'),
    path('ajax/budget/<int:budget_pk>/add-item/', views.budget_item_create_ajax, name='budget_item_create_ajax'),
    path('ajax/budget/<int:budget_pk>/add-items/', views.budget_items_create_multiple_ajax, name='budget_items_create_multiple_ajax'),
    path('ajax/budget/<int:budget_pk>/import-items/', views.budget_items_import_excel, name='budget_items_import_excel'),
    path('ajax/budget/<int:budget_pk>/download-template/', views.budget_items_download_template, name='budget_items_download_template'),
    path('ajax/categories/', views.categories_list_ajax, name='categories_list_ajax'),
]
