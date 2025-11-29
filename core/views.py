# core/views.py

from django.db.models import Sum
from .models import Pelanggan, Barang, Penyewaan
from datetime import datetime, timedelta
# Import yang dibutuhkan
from django.db.models.functions import TruncMonth 

def admin_dashboard_context(request):
    """
    Mengambil data agregasi untuk ditampilkan di dashboard Admin.
    """
    
    # --- 1. Data Cards ---
    total_pelanggan = Pelanggan.objects.count()
    total_barang = Barang.objects.count()
    
    # Total Penyewaan yang sukses (Confirmed/Completed)
    # Catatan: Jika tidak ada data, nilai ini akan 0.
    penyewaan_sukses = Penyewaan.objects.filter(
        statusSewa__in=['Confirmed', 'Completed']
    )
    total_penyewaan = penyewaan_sukses.count()
    
    # Total Pendapatan
    total_pendapatan_agg = penyewaan_sukses.aggregate(Sum('totalBayar'))
    # Pastikan total_pendapatan adalah float atau 0
    total_pendapatan = total_pendapatan_agg.get('totalBayar__sum', 0.00) or 0.00
    
    
    # --- 2. Data Grafik (Pendapatan 6 Bulan Terakhir) ---
    six_months_ago = datetime.now() - timedelta(days=180)
    
    pendapatan_per_bulan = penyewaan_sukses.filter(
        tanggalPesan__gte=six_months_ago
    ).annotate(
        month=TruncMonth('tanggalPesan')
    ).values('month').annotate(
        total=Sum('totalBayar')
    ).order_by('month')

    # Siapkan label dan data untuk Chart.js
    bulan_label = [p['month'].strftime('%b %Y') for p in pendapatan_per_bulan]
    pendapatan_bulanan = [float(p['total']) for p in pendapatan_per_bulan]
    
    # Cek apakah ada data. Jika tidak ada, buat label dummy untuk indikator
    if not bulan_label:
        bulan_label = ["Belum ada data"]
        pendapatan_bulanan = [0]
        
    context = {
        'total_pelanggan': total_pelanggan,
        'total_barang': total_barang,
        'total_penyewaan': total_penyewaan,
        'total_pendapatan': total_pendapatan,
        'pendapatan_bulanan': pendapatan_bulanan,
        'bulan_label': bulan_label,
        # Variabel untuk mengindikasikan apakah ada transaksi riil (di luar 0)
        'has_real_data': total_penyewaan > 0 or total_pendapatan > 0
    }
    
    return context