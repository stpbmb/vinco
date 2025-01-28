from django.urls import path
from . import views

app_name = 'packaging'

urlpatterns = [
    # Bottle URLs
    path('bottles/', views.list_bottles, name='list_bottles'),
    path('bottles/add/', views.add_bottle, name='add_bottle'),
    path('bottles/<int:pk>/', views.bottle_detail, name='bottle_detail'),
    path('bottles/<int:pk>/edit/', views.edit_bottle, name='edit_bottle'),
    
    # Label URLs
    path('labels/', views.list_labels, name='list_labels'),
    path('labels/add/', views.add_label, name='add_label'),
    path('labels/<int:pk>/', views.label_detail, name='label_detail'),
    path('labels/<int:pk>/edit/', views.edit_label, name='edit_label'),
    
    # Closure URLs
    path('closures/', views.list_closures, name='list_closures'),
    path('closures/add/', views.add_closure, name='add_closure'),
    path('closures/<int:pk>/', views.closure_detail, name='closure_detail'),
    path('closures/<int:pk>/edit/', views.edit_closure, name='edit_closure'),
    
    # Box URLs
    path('boxes/', views.list_boxes, name='list_boxes'),
    path('boxes/add/', views.add_box, name='add_box'),
    path('boxes/<int:pk>/', views.box_detail, name='box_detail'),
    path('boxes/<int:pk>/edit/', views.edit_box, name='edit_box'),
]
