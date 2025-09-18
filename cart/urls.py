from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='cart.index'),
    path('create/', views.create_cart, name='cart.create'),
    path('<int:cart_id>/', views.cart_detail, name='cart.detail'),
    path('<int:cart_id>/purchase/', views.purchase, name='cart.purchase'),
    path('<int:cart_id>/clear/', views.clear_cart, name='cart.clear'),
    path('<int:cart_id>/delete/', views.delete_cart, name='cart.delete'),
    path('<int:cart_id>/item/<int:item_id>/update/', views.update_item_quantity, name='cart.update_item'),
    path('<int:cart_id>/item/<int:item_id>/remove/', views.remove_item, name='cart.remove_item'),
    path('<int:id>/add/', views.add, name='cart.add'),  # Keep for backward compatibility
]