from django.urls import path
from . import views

app_name = 'harvests'

urlpatterns = [
    path('', views.HarvestListView.as_view(), name='list_harvests'),
    path('add/', views.HarvestCreateView.as_view(), name='add_harvest'),
    path('<int:pk>/', views.HarvestDetailView.as_view(), name='harvest_detail'),
    path('<int:pk>/edit/', views.HarvestUpdateView.as_view(), name='edit_harvest'),
    path('<int:pk>/delete/', views.HarvestDeleteView.as_view(), name='delete_harvest'),
    path('<int:harvest_id>/allocations/add/', views.HarvestAllocationCreateView.as_view(), name='allocation_create'),
    path('allocations/<int:pk>/edit/', views.HarvestAllocationUpdateView.as_view(), name='edit_allocation'),
    path('allocations/<int:pk>/delete/', views.HarvestAllocationDeleteView.as_view(), name='delete_allocation'),
]
