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

urlpatterns = [
    # Jika Anda memiliki URL non-admin untuk aplikasi 'core', masukkan di sini.
    # Contoh: path('', views.HomeView.as_view(), name='home'),
] + report_urls