from django.urls import path
from . import views

app_name = 'packaging'

urlpatterns = [
    # Bottle URLs
    path('bottles/', views.BottleListView.as_view(), name='list_bottles'),
    path('bottles/create/', views.BottleCreateView.as_view(), name='create_bottle'),
    path('bottles/<int:pk>/', views.BottleDetailView.as_view(), name='detail_bottle'),
    path('bottles/<int:pk>/update/', views.BottleUpdateView.as_view(), name='update_bottle'),
    
    # Box URLs
    path('boxes/', views.BoxListView.as_view(), name='list_boxes'),
    path('boxes/create/', views.BoxCreateView.as_view(), name='create_box'),
    path('boxes/<int:pk>/', views.BoxDetailView.as_view(), name='detail_box'),
    path('boxes/<int:pk>/update/', views.BoxUpdateView.as_view(), name='update_box'),
    
    # Closure URLs
    path('closures/', views.ClosureListView.as_view(), name='list_closures'),
    path('closures/create/', views.ClosureCreateView.as_view(), name='create_closure'),
    path('closures/<int:pk>/', views.ClosureDetailView.as_view(), name='detail_closure'),
    path('closures/<int:pk>/update/', views.ClosureUpdateView.as_view(), name='update_closure'),
    
    # Label URLs
    path('labels/', views.LabelListView.as_view(), name='list_labels'),
    path('labels/create/', views.LabelCreateView.as_view(), name='create_label'),
    path('labels/<int:pk>/', views.LabelDetailView.as_view(), name='detail_label'),
    path('labels/<int:pk>/update/', views.LabelUpdateView.as_view(), name='update_label'),
    
    # Bottling URLs
    path('bottlings/', views.BottlingListView.as_view(), name='list_bottlings'),
    path('bottlings/<int:pk>/', views.BottlingDetailView.as_view(), name='detail_bottling'),
    path('bottlings/add/', views.BottlingCreateView.as_view(), name='create_bottling'),
    path('bottlings/<int:pk>/edit/', views.BottlingUpdateView.as_view(), name='update_bottling'),
    path('bottlings/<int:pk>/delete/', views.delete_bottling, name='delete_bottling'),
    path('bottlings/unfinished/', views.list_unfinished_bottlings, name='list_unfinished_bottlings'),
]
