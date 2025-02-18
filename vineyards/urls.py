from django.urls import path
from . import views

app_name = 'vineyards'

urlpatterns = [
    # Vineyard URLs
    path('', views.list_vineyards, name='list_vineyards'),
    path('add/', views.add_vineyard, name='add_vineyard'),
    path('edit/<int:vineyard_id>/', views.edit_vineyard, name='edit_vineyard'),
    path('<int:vineyard_id>/', views.vineyard_detail, name='vineyard_detail'),
    path('vineyard/<int:vineyard_id>/delete/', views.delete_vineyard, name='delete_vineyard'),
    path('api/vineyards/<int:vineyard_id>/', views.vineyard_api, name='vineyard_api'),
    
    # Supplier URLs
    path('suppliers/', views.list_suppliers, name='list_suppliers'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:supplier_id>/delete/', views.delete_supplier, name='delete_supplier'),
]
