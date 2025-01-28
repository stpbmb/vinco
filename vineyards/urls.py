from django.urls import path
from . import views

urlpatterns = [
    path('vineyards/', views.list_vineyards, name='list_vineyards'),
    path('vineyards/add/', views.add_vineyard, name='add_vineyard'),
    path('vineyards/edit/<int:vineyard_id>/', views.edit_vineyard, name='edit_vineyard'),
    path('vineyards/<int:vineyard_id>/', views.vineyard_detail, name='vineyard_detail'),
    path('suppliers/', views.list_suppliers, name='list_suppliers'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('harvests/', views.list_harvests, name='list_harvests'),
    path('harvests/add/', views.add_harvest, name='add_harvest'),
    path('harvests/edit/<int:harvest_id>/', views.edit_harvest, name='edit_harvest'),
    path('harvests/<int:harvest_id>/', views.harvest_detail, name='harvest_detail'),
    path('cellars/', views.list_cellars, name='list_cellars'),
    path('cellars/add/', views.add_cellar, name='add_cellar'),
    path('cellars/edit/<int:cellar_id>/', views.edit_cellar, name='edit_cellar'),
    path('cellars/<int:cellar_id>/', views.cellar_detail, name='cellar_detail'),
    path('cellars/<int:cellar_id>/tanks/add/', views.add_tank, name='add_tank'),
    path('tanks/edit/<int:tank_id>/', views.edit_tank, name='edit_tank'),
    path('tanks/<int:tank_id>/history/', views.tank_history, name='tank_history'),
    path('harvests/<int:harvest_id>/allocations/', views.list_allocations, name='list_allocations'),
    path('harvests/<int:harvest_id>/allocations/add/', views.add_allocation, name='add_allocation'),
    path('allocations/edit/<int:allocation_id>/', views.edit_allocation, name='edit_allocation'),
]
