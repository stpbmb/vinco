from django.urls import path
from . import views

app_name = 'harvests'

urlpatterns = [
    path('', views.HarvestListView.as_view(), name='list_harvests'),
    path('add/', views.HarvestCreateView.as_view(), name='add_harvest'),
    path('<int:pk>/', views.HarvestDetailView.as_view(), name='harvest_detail'),
    path('<int:pk>/edit/', views.HarvestUpdateView.as_view(), name='edit_harvest'),
    path('<int:harvest_id>/allocate/', views.HarvestAllocationCreateView.as_view(), name='add_allocation'),
]
