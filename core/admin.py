from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F
from .models import Pelanggan, Barang, Penyewaan, DetailSewa
from django.contrib.auth.models import Group
from django.contrib.admin.sites import NotRegistered 

# Asumsi: Anda memiliki file views.py dengan fungsi admin_dashboard_context
# Jika views.py tidak ada atau tidak memiliki fungsi tersebut, baris ini akan menyebabkan error
try:
    from .views import admin_dashboard_context 
except ImportError:
    # Fungsi placeholder jika views.py.admin_dashboard_context tidak ditemukan
    def admin_dashboard_context(request):
        return {
            'total_pelanggan': 0, 'total_barang': 0, 'total_penyewaan': 0, 
            'total_pendapatan': 0, 'bulan_label': [], 'pendapatan_bulanan': []
        }
    

# ===============================================
# LANGKAH 1: UNREGISTER GROUP DARI DEFAULT SITE
# ===============================================
# Lakukan unregister dari admin.site bawaan sebelum menimpanya.
try:
    admin.site.unregister(Group)
except NotRegistered:
    pass 


# ===============================================
# LANGKAH 2: MEMBUAT DAN MENIMPA CUSTOM ADMIN SITE
# ===============================================
class CustomAdminSite(admin.AdminSite):
    index_template = 'admin/custom_index.html'
    site_header = 'ADMINISTRASI PENYEWAAN'
    site_title = 'Admin Penyewaan'

    def index(self, request, extra_context=None):
        # Memuat data agregasi dari fungsi views
        context = admin_dashboard_context(request) 
        
        if extra_context:
            context.update(extra_context)
            
        return super().index(request, context)

# Instansiasi Custom Admin Site
custom_admin_site = CustomAdminSite(name='custom_admin')
# Menimpa variabel admin.site global dengan instance kustom
admin.site = custom_admin_site 


# ===============================================
# LANGKAH 3: PENDAFTARAN MODEL KE CUSTOM ADMIN SITE
# ===============================================

# --- Admin Class untuk Pelanggan ---
@admin.register(Pelanggan, site=custom_admin_site)
class PelangganAdmin(admin.ModelAdmin):
    list_display = ('idPelanggan', 'namaPelanggan', 'noHp', 'aksi_link') 
    search_fields = ('namaPelanggan', 'noHp')
    list_filter = ('namaPelanggan',)
    
    def aksi_link(self, obj):
        # Menggunakan idPelanggan
        edit_url = f'/admin/core/pelanggan/{obj.idPelanggan}/change/' 
        edit_icon = f'<a href="{edit_url}" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_url = f'/admin/core/pelanggan/{obj.idPelanggan}/delete/'
        delete_icon = f'<a href="{delete_url}" title="Hapus"><i class="fas fa-trash-alt" style="color: red;"></i></a>'
        return format_html(f'{edit_icon} &nbsp; {delete_icon}')
    aksi_link.short_description = 'Aksi'


# --- Admin Class untuk Barang ---
@admin.register(Barang, site=custom_admin_site)
class BarangAdmin(admin.ModelAdmin):
    list_display = ('idBarang', 'namaBarang', 'harga', 'stok', 'ukuran', 'foto_preview', 'aksi_link')
    search_fields = ('namaBarang',)
    list_filter = ('ukuran',)
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.foto.url)
        return "No Image"
    foto_preview.short_description = 'Foto'
    
    def aksi_link(self, obj):
        # Menggunakan idBarang
        edit_url = f'/admin/core/barang/{obj.idBarang}/change/' 
        edit_icon = f'<a href="{edit_url}" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_url = f'/admin/core/barang/{obj.idBarang}/delete/'
        delete_icon = f'<a href="{delete_url}" title="Hapus"><i class="fas fa-trash-alt" style="color: red;"></i></a>'
        return format_html(f'{edit_icon} &nbsp; {delete_icon}')
    aksi_link.short_description = 'Aksi'
    

# --- Inline dan Admin Class untuk Penyewaan ---
class DetailSewaInline(admin.TabularInline):
    model = DetailSewa
    fields = ('idBarang', 'jumlahBarang', 'subTotal')
    # readonly_fields adalah kunci untuk mencegah pengguna mengedit subTotal
    readonly_fields = ('subTotal',) 
    extra = 1

    
@admin.register(Penyewaan, site=custom_admin_site)
class PenyewaanAdmin(admin.ModelAdmin):
    inlines = [DetailSewaInline]
    list_display = (
         'idPenyewaan', 'tanggalPesan', 'tanggalAcara', 'durasiSewa', 'totalBayar', 'statusSewa', 'idPelanggan', 'aksi_link'
    )
    search_fields = ('idPelanggan__namaPelanggan', 'statusSewa')
    list_filter = ('statusSewa', 'tanggalAcara')
    
    fieldsets = (
        (None, {
            'fields': ('idPelanggan', 'tanggalAcara', 'tanggalPembongkaran', 'durasiSewa', 'alamatPemasangan')
        }),
        ('Detail Pembayaran dan Status', {
            # totalBayar harus ada di fields agar bisa ditampilkan, tapi di readonly_fields
            'fields': ('totalBayar', 'statusSewa', 'feedback'), 
            'classes': ('collapse',),
        })
    )
    # Tampilkan totalBayar dan tanggalPesan (auto_now_add) sebagai read-only di form
    readonly_fields = ('totalBayar', 'tanggalPesan')
    
    def calculate_total_bayar(self, penyewaan_instance):
        """Menghitung totalBayar dari semua subTotal di DetailSewa."""
        
        # Agregasi semua subTotal (yang sudah dihitung saat DetailSewa.save())
        total_sum = penyewaan_instance.detailsewa_set.aggregate(
            total=Sum(F('subTotal'))
        )['total']
        
        # Perbarui totalBayar di objek Penyewaan
        if total_sum is not None:
            # Pastikan totalBayar adalah DecimalField yang valid sebelum disimpan
            penyewaan_instance.totalBayar = total_sum
            penyewaan_instance.save(update_fields=['totalBayar'])

    def save_model(self, request, obj, form, change):
        # 1. Simpan objek Penyewaan terlebih dahulu (Ini penting untuk mendapatkan PK/ID)
        super().save_model(request, obj, form, change)
        
        if change:
             # Untuk kasus edit, kita panggil calculate_total_bayar di sini juga
             self.calculate_total_bayar(obj)
        
    def save_formset(self, request, form, formset, change):
        # 1. Simpan inline commit=False
        instances = formset.save(commit=False)
        for instance in instances:
            # Panggil method save() di model DetailSewa.
            # Sekarang, method save() DetailSewa akan menghitung subTotal DAN menyesuaikan stok.
            if isinstance(instance, DetailSewa):
                instance.save() 
        
        # 2. Simpan relasi Many-to-Many jika ada (meskipun tidak ada di sini, ini adalah praktik baik)
        formset.save_m2m()
        
        # 3. Handle penghapusan inlines (Ini akan memanggil method delete() di model DetailSewa, yang mengembalikan stok)
        for obj in formset.deleted_objects:
            obj.delete()

        # 4. Setelah semua DetailSewa tersimpan/dihapus, hitung ulang totalBayar Penyewaan utama.
        if form.instance.pk:
            self.calculate_total_bayar(form.instance)
        
    
    def aksi_link(self, obj):
        # Menggunakan idPenyewaan
        edit_url = f'/admin/core/penyewaan/{obj.idPenyewaan}/change/' 
        edit_icon = f'<a href="{edit_url}" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_url = f'/admin/core/penyewaan/{obj.idPenyewaan}/delete/'
        delete_icon = f'<a href="{delete_url}" title="Hapus"><i class="fas fa-trash-alt" style="color: red;"></i></a>'
        return format_html(f'{edit_icon} &nbsp; {delete_icon}')
    aksi_link.short_description = 'Aksi'