from django.urls import path
from . import views

urlpatterns = [
    
path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('admin-dashboard/order-status/<int:order_id>/', views.admin_update_order_status, name='admin_update_order_status'),
path('admin-dashboard/delete-product/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
path('track-order/', views.track_order, name='track_order'),
]