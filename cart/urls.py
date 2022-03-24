from django.urls import path

from cart import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_to_cart, name='add_cart'),
    path('remove_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_cart'),
    path('remove_cart_item/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
]
