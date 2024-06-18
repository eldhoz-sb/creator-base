
from django.urls import path
from shop import views
from .views import cart,add_to_cart

urlpatterns = [
    path('home/', views.index, name='shop-index'),
    path('create_product/', views.create_product, name='create_product'),
    path('products/', views.userindex, name='shop-userindex'),
    path('product/<int:product_id>/<slug:product_slug>/',
        views.show_product, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/<int:cart_id>/', views.show_cart, name='show_cart'),
    path('cart/', cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
]