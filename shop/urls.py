from django.urls import path
from . import views

urlpatterns = [
    # Template URLs
    path('', views.index_view, name='index'),
    path('product/<int:product_id>/', views.product_page_view, name='product_page'),
    path('cart/', views.cart_page_view, name='cart_page'),
    path('checkout/', views.checkout_page_view, name='checkout_page'),
    path('login/', views.login_page_view, name='login_page'),
    path('register/', views.register_page_view, name='register_page'),
    path('orders/', views.orders_page_view, name='orders_page'),

    # API URLs
    path('api/register/', views.api_register, name='api_register'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/auth-status/', views.api_auth_status, name='api_auth_status'),
    path('api/products/', views.api_products, name='api_products'),
    path('api/products/<int:product_id>/', views.api_product_detail, name='api_product_detail'),
    path('api/cart/', views.api_cart, name='api_cart'),
    path('api/checkout/', views.api_checkout, name='api_checkout'),
    path('api/orders/', views.api_orders, name='api_orders'),
]
