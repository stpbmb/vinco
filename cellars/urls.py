from django.urls import path
from . import views

app_name = 'cellars'

urlpatterns = [
    # Cellar URLs
    path('', views.CellarListView.as_view(), name='list_cellars'),
    path('add/', views.CellarCreateView.as_view(), name='add_cellar'),
    path('<int:pk>/', views.CellarDetailView.as_view(), name='cellar_detail'),
    path('<int:pk>/edit/', views.CellarUpdateView.as_view(), name='edit_cellar'),

    # Tank URLs
    path('tanks/', views.TankListView.as_view(), name='list_tanks'),
    path('<int:cellar_id>/tanks/add/', views.TankCreateView.as_view(), name='add_tank'),
    path('tanks/<int:pk>/', views.TankDetailView.as_view(), name='tank_detail'),
    path('tanks/<int:pk>/edit/', views.TankUpdateView.as_view(), name='edit_tank'),
    path('tanks/<int:pk>/history/', views.TankHistoryView.as_view(), name='tank_history'),
    path('tanks/transfer/', views.TransferWineView.as_view(), name='transfer_wine'),

    # Allocation URLs
    path('allocations/', views.AllocationListView.as_view(), name='list_allocations'),
    path('allocations/add/', views.AllocationCreateView.as_view(), name='add_allocation'),
]
