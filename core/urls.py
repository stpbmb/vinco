from django.urls import path
from .views.dashboard import DashboardView

app_name = 'core'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),  # Only keep one dashboard URL
]
