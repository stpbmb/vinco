from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    path('select/', views.organization_select, name='select'),
]
