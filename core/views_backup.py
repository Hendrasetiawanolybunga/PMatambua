from django.db.models import Sum
from django.db.models.functions import TruncMonth 
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from datetime import datetime, timedelta
from calendar import month_abbr 

# --- Import untuk Laporan PDF menggunakan ReportLab ---
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
# ----------------------------------------------------

# Import Models
from .models import Pelanggan, Barang, Penyewaan, DetailSewa

# Import Tools untuk Laporan
from django_tables2 import SingleTableView
from django_filters.views import FilterView 
from django_tables2.rows import BoundRow 

# Import Table dan Filter yang sudah Anda buat (Diasumsikan ada di core/tables.py dan core/filters.py)
from .tables import PenyewaanReportTable, KeuanganReportTable, DetailBarangReportTable, PelangganReportTable
from .filters import PenyewaanFilter, KeuanganFilter, DetailBarangFilter


# =================================================================
# FUNGSI CONTEXT DASHBOARD ADMIN
# =================================================================
def admin_dashboard_context(request):
    """
    Mengambil data agregasi untuk ditampilkan di dashboard Admin.
    Diperbarui untuk menampilkan data 6 bulan terakhir secara konsisten.
    """
    
    # --- 1. Data Cards ---
    total_pelanggan = Pelanggan.objects.count()
    total_barang = Barang.objects.count()
    
    # Total Penyewaan yang sukses (Confirmed/Completed)
    penyewaan_sukses = Penyewaan.objects.filter(
        statusSewa__in=['Confirmed', 'Completed']
    )
    total_penyewaan = penyewaan_sukses.count()
    
    # Total Pendapatan
    total_pendapatan_agg = penyewaan_sukses.aggregate(Sum('totalBayar'))
    total_pendapatan = total_pendapatan_agg.get('totalBayar__sum', 0.00) or 0.00
    
    
    # --- 2. Data Grafik (Pendapatan 6 Bulan Terakhir) ---
    
    today = datetime.now()
    
    # 2.1. Tentukan Tanggal Mulai (6 bulan terakhir termasuk bulan ini)
    # Dapatkan bulan saat ini (hanya tahun dan bulan)
    current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Mundur 5 bulan untuk mendapatkan awal periode (6 bulan termasuk bulan ini)
    five_months_ago = current_month_start
    for i in range(5):
        # Cari hari pertama bulan sebelumnya
        if five_months_ago.month == 1:
            five_months_ago = five_months_ago.replace(year=five_months_ago.year - 1, month=12)
        else:
            five_months_ago = five_months_ago.replace(month=five_months_ago.month - 1)
    
    # print(f"Current month start: {current_month_start}")
    # print(f"Five months ago (start of range): {five_months_ago}")
    
    # Gunakan five_months_ago sebagai awal periode
    start_of_range = five_months_ago
        
    
    # 2.2. Ambil data aktual dari database
    # print(f"Filtering rentals from date: {start_of_range}")
    filtered_rentals = penyewaan_sukses.filter(tanggalPesan__gte=start_of_range)
    # print(f"Found {filtered_rentals.count()} rentals in the date range")
    
    # Print some sample rental data for debugging
    # sample_rentals = filtered_rentals[:5]
    # for rental in sample_rentals:
    #     print(f"Rental ID: {rental.idPenyewaan}, Date: {rental.tanggalPesan}, Status: {rental.statusSewa}, Total: {rental.totalBayar}")
    
    pendapatan_per_bulan_qs = filtered_rentals.annotate(
        month=TruncMonth('tanggalPesan')
    ).values('month').annotate(
        total=Sum('totalBayar')
    ).order_by('month')
    
    # print(f"Aggregation query returned {pendapatan_per_bulan_qs.count()} grouped records")
    # for item in pendapatan_per_bulan_qs:
    #     print(f"  Month: {item['month']} (type: {type(item['month'])}), Total: {item['total']}")
    
    # Improved data processing to ensure correct data types
    pendapatan_dict = {}
    for p in pendapatan_per_bulan_qs:
        month_value = p['month']
        total_value = p['total']
        
        # Convert month to date if it's datetime
        if isinstance(month_value, datetime):
            key = month_value.date()
        else:
            key = month_value
            
        # print(f"Processing month_value: {month_value} (type: {type(month_value)}), converted key: {key} (type: {type(key)})")
            
        # Ensure total value is converted to float correctly
        if total_value is not None:
            pendapatan_dict[key] = float(total_value)
        else:
            pendapatan_dict[key] = 0.0
            
        # print(f"Aggregated data - Month: {key}, Revenue: {pendapatan_dict[key]}")

    
    # 2.3. Generate 6 bulan lengkap (dari 6 bulan lalu hingga bulan ini)
    bulan_label = []
    pendapatan_bulanan = []
    
    # Mulai dari bulan ke-5 yang lalu (awal periode)
    current_date = start_of_range 
    
    # print(f"Generating data for 6 months starting from: {start_of_range}")
    # print(f"Keys in pendapatan_dict: {list(pendapatan_dict.keys())}")
    
    # Kita iterasi sebanyak 6 bulan
    for i in range(6):
        
        # Format label: Singkatan Bulan Tahun (e.g., Jun 2025)
        label = current_date.strftime('%b %Y') 
        bulan_label.append(label)
        
        # Key pencarian harus dalam format datetime.date
        data_key = current_date.date() 
        
        # Debug the key matching
        # print(f"Checking month {i+1}: {data_key} (looking for this key in dict)")
        # print(f"Available keys: {list(pendapatan_dict.keys())}")
        
        # Try to find matching key (handle potential type mismatches)
        pendapatan = 0.0
        for dict_key, dict_value in pendapatan_dict.items():
            # Compare dates regardless of whether they're date or datetime objects
            if hasattr(dict_key, 'date') and dict_key.date() == data_key:
                pendapatan = dict_value
                break
            elif dict_key == data_key:
                pendapatan = dict_value
                break
                
        # print(f"  Found revenue: {pendapatan}")
        pendapatan_bulanan.append(pendapatan)
        
        # Maju ke bulan berikutnya dengan cara yang lebih robust
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
            
    # Ensure we always have 6 data points, even if no data exists
    if len(pendapatan_bulanan) == 0:
        pendapatan_bulanan = [0.0] * 6
            
    
    # Debug print for troubleshooting
    # print(f"Dashboard data - Total rentals: {total_penyewaan}, Total revenue: {total_pendapatan}")
    # print(f"Monthly labels: {bulan_label}")
    # print(f"Monthly revenue: {pendapatan_bulanan}")
    
    context = {
        'total_pelanggan': total_pelanggan,
        'total_barang': total_barang,
        'total_penyewaan': total_penyewaan,
        'total_pendapatan': total_pendapatan,
        'pendapatan_bulanan': pendapatan_bulanan,
        'bulan_label': bulan_label,
        'has_real_data': total_penyewaan > 0 or total_pendapatan > 0
    }
    
    return context


# =================================================================
# FUNGSI MIXIN DAN VIEW UNTUK LAPORAN (HTML/Filter View)
# =================================================================

class AdminReportMixin:
    """Mixin untuk mengatur template AdminLTE dan pembatasan akses."""
    template_name = 'admin/report_template.html'
    
    @classmethod
    def as_view(cls, **initkwargs):
        """Memastikan hanya staff/admin yang bisa mengakses laporan."""
        view = super().as_view(**initkwargs)
        return staff_member_required(view)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.report_title
        
        # 🔥 PENTING: Untuk mempertahankan sidebar, kita beri tahu Jazzmin aplikasi apa yang aktif.
        self.request.current_app = 'core'
        context['current_app'] = 'core'
        
        # Tambahkan filter ke context agar bisa digunakan di tombol PDF
        safe_params = {k: v for k, v in self.request.GET.items() if k not in ['page', 'sort']}
        context['current_filter_params'] = "&" + "&".join(f"{k}={v}" for k, v in safe_params.items())
        return context


# -----------------------------------------------------------------
# 1. Laporan Penyewaan (HTML View)
# -----------------------------------------------------------------
class PenyewaanReportView(AdminReportMixin, FilterView, SingleTableView):
    model = Penyewaan
    table_class = PenyewaanReportTable
    filterset_class = PenyewaanFilter
    report_title = "Laporan Data Penyewaan"
    
# -----------------------------------------------------------------
# 2. Laporan Keuangan (HTML View)
# -----------------------------------------------------------------
class KeuanganReportView(AdminReportMixin, FilterView, SingleTableView):
    model = Penyewaan
    table_class = KeuanganReportTable
    filterset_class = KeuanganFilter
    report_title = "Laporan Keuangan (Pendapatan)"

    def get_queryset(self):
        # Default Querset hanya Confirmed/Completed
        queryset = super().get_queryset().filter(statusSewa__in=['Confirmed', 'Completed'])
        return queryset.order_by('-tanggalPesan') # Pengurutan default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_pendapatan_agg = self.object_list.aggregate(Sum('totalBayar'))
        total_pendapatan = total_pendapatan_agg.get('totalBayar__sum', 0.00) or 0.00
        context['total_pendapatan'] = total_pendapatan
        return context


# -----------------------------------------------------------------
# 3. Laporan Barang (Status Barang - HTML View)
# -----------------------------------------------------------------
class BarangReportView(AdminReportMixin, FilterView, SingleTableView):
    model = DetailSewa
    table_class = DetailBarangReportTable
    filterset_class = DetailBarangFilter
    report_title = "Laporan Status Barang Sewa"

    def get_queryset(self):
        return super().get_queryset().select_related('idPenyewaan', 'idBarang').order_by('idPenyewaan')

# -----------------------------------------------------------------
# 4. Laporan Data Pelanggan (HTML View)
# -----------------------------------------------------------------
class PelangganReportView(AdminReportMixin, SingleTableView):
    model = Pelanggan
    table_class = PelangganReportTable
    report_title = "Laporan Data Pelanggan"


# =================================================================
# FUNGSI PDF GENERATOR (REPORTLAB)
# =================================================================

def generate_reportlab_pdf(request, filterset_class, model_class, table_class, title, is_keuangan=False):
    """Fungsi pembantu untuk menghasilkan PDF menggunakan ReportLab."""
    
    # 1. Siapkan Response dan Document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{title.replace(" ", "_")}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    Story = []

    # 2. Ambil Data dan Filter
    queryset = model_class.objects.all()
    
    # Khusus untuk Keuangan, filter data sukses sejak awal
    if model_class == Penyewaan and is_keuangan:
        queryset = queryset.filter(statusSewa__in=['Confirmed', 'Completed'])
    
    # Inisialisasi FilterSet
    f = filterset_class(request.GET, queryset=queryset)
    
    # Dapatkan field pengurutan yang aman (safe ordering field)
    ordering_field = None
    try:
        ordering_field = getattr(table_class.Meta, 'order_by', None)
        
        if ordering_field is None:
            ordering_field = table_class.Meta.fields[0]
            
    except (AttributeError, IndexError):
        ordering_field = 'pk'
    
    # Lakukan pengurutan dengan field yang aman
    if ordering_field:
        filtered_queryset = f.qs.order_by(ordering_field)
    else:
        filtered_queryset = f.qs.all()
    
    # 3. Judul
    p_title = Paragraph(title, styles['Title'])
    Story.append(p_title)
    Story.append(Spacer(1, 0.25 * inch))

    # 4. Data Tabel (Header dan Data)
    table_instance = table_class(filtered_queryset)
    
    # Header Tabel (verbose_name dari Table Class)
    header = [column.header for column in table_instance.columns]
    data = [header]
    
    # Data Baris
    for row in filtered_queryset: 
        bound_row = BoundRow(row, table_instance)
        
        data_row = []
        for column in table_instance.columns:
            rendered_value = bound_row.get_cell(column.name)
            data_row.append(str(rendered_value))

        data.append(data_row)
        
    # 5. Buat dan Gaya Tabel
    table = Table(data)
    
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')), # Header Biru
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige), # Baris data
    ])
    
    table.setStyle(style)
    Story.append(table)
    Story.append(Spacer(1, 0.5 * inch))

    # 6. Total Pendapatan (Khusus Keuangan)
    if is_keuangan:
        total_pendapatan_agg = filtered_queryset.aggregate(Sum('totalBayar'))
        total_pendapatan = total_pendapatan_agg.get('totalBayar__sum', 0.00) or 0.00
        
        # Format angka agar sesuai standar Indonesia (misal: 1.000.000,00)
        total_formatted = "Rp {:,.2f}".format(total_pendapatan).replace(",", "X").replace(".", ",").replace("X", ".")
        
        total_text = f"<b>Total Pendapatan Terfilter:</b> {total_formatted}"
        Story.append(Paragraph(total_text, styles['Normal']))


    # 7. Build Dokumen
    doc.build(Story)
    return response

# -----------------------------------------------------------------
# PDF View Laporan Penyewaan
# -----------------------------------------------------------------
@staff_member_required
def PenyewaanPDFView(request):
    return generate_reportlab_pdf(
        request, 
        PenyewaanFilter, 
        Penyewaan, 
        PenyewaanReportTable, 
        "Laporan Data Penyewaan"
    )

# -----------------------------------------------------------------
# PDF View Laporan Keuangan
# -----------------------------------------------------------------
@staff_member_required
def KeuanganPDFView(request):
    return generate_reportlab_pdf(
        request, 
        KeuanganFilter, 
        Penyewaan, 
        KeuanganReportTable, 
        "Laporan Keuangan (Pendapatan)",
        is_keuangan=True
    )

# -----------------------------------------------------------------
# PDF View Laporan Status Barang
# -----------------------------------------------------------------
@staff_member_required
def BarangPDFView(request):
    # Catatan: DetailSewa sudah menangani join ke Barang
    return generate_reportlab_pdf(
        request, 
        DetailBarangFilter, 
        DetailSewa, 
        DetailBarangReportTable, 
        "Laporan Status Barang Sewa"
    )

# -----------------------------------------------------------------
# PDF View Laporan Pelanggan
# -----------------------------------------------------------------
@staff_member_required
def PelangganPDFView(request):
    # Buat kelas filter kosong untuk Pelanggan jika tidak ada filter kustom
    class DummyFilterSet:
        def __init__(self, *args, **kwargs):
             # Lakukan pengurutan default di sini atau biarkan Table.Meta.order_by menanganinya
            self.qs = Pelanggan.objects.all()
    
    return generate_reportlab_pdf(
        request, 
        DummyFilterSet, 
        Pelanggan, 
        PelangganReportTable, 
        "Laporan Data Pelanggan"
    )
# =================================================================
# CUSTOMER-FACING VIEWS
# =================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import datetime, date, timedelta
from django.contrib.humanize.templatetags.humanize import intcomma

def get_cart(request):
    """Get cart from session or initialize empty cart"""
    cart = request.session.get('cart', {})
    return cart

def save_cart(request, cart):
    """Save cart to session"""
    request.session['cart'] = cart
    request.session.modified = True

def get_cart_count(request):
    """Get total number of items in cart"""
    cart = get_cart(request)
    return sum(item['quantity'] for item in cart.values())

def home_view(request):
    """Display catalog of available products"""
    barang_list = Barang.objects.filter(stok__gt=0).order_by('namaBarang')
    
    context = {
        'barang_list': barang_list,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'customer/home.html', context)

def add_to_cart(request, barang_id):
    """Add item to cart"""
    if request.method == 'POST':
        try:
            barang = get_object_or_404(Barang, idBarang=barang_id)
            quantity = int(request.POST.get('quantity', 1))
            
            # Validate quantity
            if quantity <= 0:
                messages.error(request, 'Jumlah barang harus lebih dari 0.')
                return redirect('customer_home')
            
            if quantity > barang.stok:
                messages.error(request, f'Maaf, stok hanya tersedia {barang.stok} unit.')
                return redirect('customer_home')
            
            # Get cart from session
            cart = get_cart(request)
            
            # Add or update item in cart
            if str(barang_id) in cart:
                # Check if total quantity would exceed stock
                current_qty = cart[str(barang_id)]['quantity']
                if current_qty + quantity > barang.stok:
                    messages.error(request, f'Maaf, stok hanya tersedia {barang.stok} unit. Anda sudah memiliki {current_qty} unit di keranjang.')
                    return redirect('customer_home')
                cart[str(barang_id)]['quantity'] += quantity
            else:
                cart[str(barang_id)] = {
                    'barang_id': barang_id,
                    'quantity': quantity,
                    'harga': float(barang.harga),
                    'nama': barang.namaBarang,
                }
            
            # Save cart to session
            save_cart(request, cart)
            messages.success(request, f'{barang.namaBarang} berhasil ditambahkan ke keranjang.')
            
        except ValueError:
            messages.error(request, 'Jumlah barang tidak valid.')
        except Exception as e:
            messages.error(request, 'Terjadi kesalahan saat menambahkan barang ke keranjang.')
    
    return redirect('customer_home')

def checkout_view(request):
    """Display checkout page with cart items and rental form"""
    cart = get_cart(request)
    
    # Prepare cart items with full barang objects and calculated subtotals
    cart_items = []
    total_amount = 0
    
    for item_id, item_data in cart.items():
        try:
            barang = Barang.objects.get(idBarang=item_data['barang_id'])
            subtotal = barang.harga * item_data['quantity']
            total_amount += subtotal
            
            cart_items.append({
                'barang': barang,
                'quantity': item_data['quantity'],
                'subtotal': subtotal,
            })
        except Barang.DoesNotExist:
            # Remove invalid items from cart
            del cart[item_id]
            save_cart(request, cart)
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'today': date.today().strftime('%Y-%m-%d'),
        'cart_count': get_cart_count(request),
    }
    return render(request, 'customer/checkout.html', context)

@transaction.atomic
def process_rental(request):
    """Process the rental form and create penyewaan and detailsewa records"""
    if request.method == 'POST':
        try:
            # Get cart
            cart = get_cart(request)
            if not cart:
                messages.error(request, 'Keranjang Anda kosong. Silakan tambahkan barang terlebih dahulu.')
                return redirect('customer_home')
            
            # Get form data
            nama_pelanggan = request.POST.get('namaPelanggan', '').strip()
            no_hp = request.POST.get('noHp', '').strip()
            alamat_pemasangan = request.POST.get('alamatPemasangan', '').strip()
            tanggal_acara_str = request.POST.get('tanggalAcara', '')
            durasi_sewa_str = request.POST.get('durasiSewa', '')
            
            # Validate required fields
            if not all([nama_pelanggan, no_hp, alamat_pemasangan, tanggal_acara_str, durasi_sewa_str]):
                messages.error(request, 'Semua field wajib diisi.')
                return redirect('checkout')
            
            # Validate and parse tanggal_acara
            try:
                tanggal_acara = datetime.strptime(tanggal_acara_str, '%Y-%m-%d').date()
                if tanggal_acara < date.today():
                    messages.error(request, 'Tanggal acara harus hari ini atau di masa depan.')
                    return redirect('checkout')
            except ValueError:
                messages.error(request, 'Format tanggal acara tidak valid.')
                return redirect('checkout')
            
            # Validate and parse durasi_sewa
            try:
                durasi_sewa = int(durasi_sewa_str)
                if durasi_sewa <= 0:
                    messages.error(request, 'Durasi sewa harus lebih dari 0 hari.')
                    return redirect('checkout')
            except ValueError:
                messages.error(request, 'Durasi sewa harus berupa angka.')
                return redirect('checkout')
            
            # Calculate tanggal_pembongkaran
            tanggal_pembongkaran = tanggal_acara + timedelta(days=durasi_sewa)
            
            # Check if all items in cart are still available
            for item_id, item_data in cart.items():
                try:
                    barang = Barang.objects.get(idBarang=item_data['barang_id'])
                    if item_data['quantity'] > barang.stok:
                        messages.error(request, f'Stok untuk {barang.namaBarang} tidak mencukupi. Silakan perbarui keranjang Anda.')
                        return redirect('checkout')
                except Barang.DoesNotExist:
                    messages.error(request, 'Ada barang dalam keranjang yang tidak lagi tersedia. Silakan perbarui keranjang Anda.')
                    return redirect('checkout')
            
            # Handle Pelanggan - Check if exists, create if not
            pelanggan, created = Pelanggan.objects.get_or_create(
                noHp=no_hp,
                defaults={'namaPelanggan': nama_pelanggan}
            )
            # If pelanggan exists but name is different, update name
            if not created and pelanggan.namaPelanggan != nama_pelanggan:
                pelanggan.namaPelanggan = nama_pelanggan
                pelanggan.save()
            
            # Create Penyewaan
            penyewaan = Penyewaan.objects.create(
                idPelanggan=pelanggan,
                tanggalAcara=tanggal_acara,
                durasiSewa=durasi_sewa,
                alamatPemasangan=alamat_pemasangan,
                tanggalPembongkaran=tanggal_pembongkaran,
                statusSewa='Pending',  # Default status
                totalBayar=None,  # Will be calculated by admin
            )
            
            # Create DetailSewa for each item in cart
            for item_id, item_data in cart.items():
                barang = Barang.objects.get(idBarang=item_data['barang_id'])
                DetailSewa.objects.create(
                    idPenyewaan=penyewaan,
                    idBarang=barang,
                    jumlahBarang=item_data['quantity'],
                    subTotal=None,  # Will be calculated by DetailSewa.save()
                    statusBarang='Baik',  # Default status
                )
            
            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True
            
            # Success message
            messages.success(request, f'Sewa berhasil diajukan dengan ID #{penyewaan.idPenyewaan}. Silakan tunggu konfirmasi dari admin.')
            return redirect('history_lookup')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat memproses sewa: {str(e)}')
            return redirect('checkout')
    
    return redirect('checkout')

def history_lookup_view(request):
    """Display form to lookup rental history and show results"""
    penyewaan_list = []
    
    if request.method == 'POST':
        no_hp = request.POST.get('noHp', '').strip()
        if no_hp:
            try:
                # Get pelanggan by noHp
                pelanggan = Pelanggan.objects.get(noHp=no_hp)
                # Get all penyewaan for this pelanggan
                penyewaan_list = Penyewaan.objects.filter(idPelanggan=pelanggan).order_by('-tanggalPesan')
            except Pelanggan.DoesNotExist:
                messages.error(request, 'Tidak ditemukan riwayat sewa dengan nomor HP tersebut.')
        else:
            messages.error(request, 'Silakan masukkan nomor HP.')
    
    context = {
        'penyewaan_list': penyewaan_list,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'customer/history_lookup.html', context)

def history_detail_view(request, penyewaan_id):
    """Display detailed information for a specific rental"""
    penyewaan = get_object_or_404(Penyewaan, idPenyewaan=penyewaan_id)
    detail_sewa_list = DetailSewa.objects.filter(idPenyewaan=penyewaan)
    
    context = {
        'penyewaan': penyewaan,
        'detail_sewa_list': detail_sewa_list,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'customer/history_detail.html', context)
