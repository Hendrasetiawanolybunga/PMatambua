# core/urls.py

from django.urls import path
from . import views # Pastikan views mengimpor semua View yang diperlukan

# Definisikan URL Laporan
# Catatan: Karena di-include di path('admin/', ...), semua URL ini 
# secara efektif akan diakses melalui /admin/laporan/...
report_urls = [
    # --------------------------------------------------------
    # HTML Views (Class-Based Views) - Untuk tampilan laporan interaktif
    # --------------------------------------------------------
    path('laporan/penyewaan/', views.PenyewaanReportView.as_view(), name='report_penyewaan'),
    path('laporan/keuangan/', views.KeuanganReportView.as_view(), name='report_keuangan'),
    path('laporan/barang/', views.BarangReportView.as_view(), name='report_barang'),
    path('laporan/pelanggan/', views.PelangganReportView.as_view(), name='report_pelanggan'),
    
    # --------------------------------------------------------
    # PDF Views (Function-Based Views) - Untuk menggenerate PDF
    # --------------------------------------------------------
    # Pastikan ini adalah fungsi biasa, bukan Class-Based View, 
    # oleh karena itu tidak menggunakan .as_view()
    path('laporan/penyewaan/pdf/', views.PenyewaanPDFView, name='report_penyewaan_pdf'), 
    path('laporan/keuangan/pdf/', views.KeuanganPDFView, name='report_keuangan_pdf'),
    path('laporan/barang/pdf/', views.BarangPDFView, name='report_barang_pdf'),
    path('laporan/pelanggan/pdf/', views.PelangganPDFView, name='report_pelanggan_pdf'),
]

# URL patterns for customer-facing views
pelanggan_urls = [
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
]

urlpatterns = [
    # Jika Anda memiliki URL non-admin untuk aplikasi 'core', masukkan di sini.
    # Contoh: path('', views.HomeView.as_view(), name='home'),
] + report_urls + pelanggan_urls