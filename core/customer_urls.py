from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='customer_home'),
    path('cart/add/<int:barang_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:barang_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:barang_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/process/', views.process_rental, name='process_rental'),
    path('history/lookup/', views.history_lookup_view, name='history_lookup'),
    path('history/detail/<int:penyewaan_id>/', views.history_detail_view, name='history_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]