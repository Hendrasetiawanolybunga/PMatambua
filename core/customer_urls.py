from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_pelanggan, name='home_pelanggan'),
    path('register/', views.register_pelanggan, name='register_pelanggan'),
    path('login/', views.login_pelanggan, name='login_pelanggan'),
    path('logout/', views.logout_pelanggan, name='logout_pelanggan'),
    path('barang/', views.katalog_barang, name='katalog_barang'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_checkout, name='process_checkout'),
    path('history/', views.rental_history, name='rental_history'),
    path('history/detail/<int:pk>/', views.rental_detail, name='rental_detail'),
    path('akun/', views.akun_pelanggan, name='akun_pelanggan'),
]