# core/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F
from .models import Pelanggan, Barang, Penyewaan, DetailSewa
from django.contrib.auth.models import Group, User # Penting: Import User
from django.contrib.admin.sites import NotRegistered 
from django.urls import reverse # Diperlukan untuk membuat URL link laporan
from django.contrib.humanize.templatetags.humanize import intcomma

# Asumsi: Anda memiliki file views.py dengan fungsi admin_dashboard_context
try:
    from .views import admin_dashboard_context 
except ImportError:
    # Fungsi placeholder jika views.py.admin_dashboard_context tidak ditemukan
    def admin_dashboard_context(request):
        return {
            'total_pelanggan': 0, 'total_barang': 0, 'total_penyewaan': 0, 
            'total_pendapatan': 0, 'bulan_label': [], 'pendapatan_bulanan': []
        }
    
# --- Langkah 1: UNREGISTER GROUP DAN USER DARI DEFAULT SITE ---
try:
    admin.site.unregister(Group)
except NotRegistered:
    pass 
    
try:
    admin.site.unregister(User)
except NotRegistered:
    pass


# --- Langkah 2: MEMBUAT DAN MENIMPA CUSTOM ADMIN SITE ---
class CustomAdminSite(admin.AdminSite):
    index_template = 'admin/custom_index.html'
    site_header = 'ADMINISTRASI PENYEWAAN'
    site_title = 'Admin Penyewaan'

    def index(self, request, extra_context=None):
        context = admin_dashboard_context(request) 
        
        if extra_context:
            context.update(extra_context)
            
        return super().index(request, context)

    # PERBAIKAN UTAMA: Memastikan app_list bukan None dan menambahkan Laporan
    def get_app_list(self, request, app_label=None):
        
        app_list = super().get_app_list(request)
        
        # PERBAIKAN 1: Mencegah 'NoneType' object is not iterable dari Jazzmin
        if app_list is None:
            app_list = []

        # 1. Definisikan Links Laporan Kustom (Nama URL tanpa 'admin:' karena di-include di path 'admin/')
        report_models = [
            {
                'name': 'Laporan Penyewaan',
                'object_name': 'laporan_penyewaan',
                'perms': {'view': request.user.has_perm('core.view_penyewaan')},
                'admin_url': reverse('report_penyewaan'), # PERBAIKAN 2: Hapus 'admin:'
            },
            {
                'name': 'Laporan Keuangan',
                'object_name': 'laporan_keuangan',
                'perms': {'view': request.user.has_perm('core.view_penyewaan')},
                'admin_url': reverse('report_keuangan'),
            },
            {
                'name': 'Laporan Status Barang',
                'object_name': 'laporan_barang',
                'perms': {'view': request.user.has_perm('core.view_detailsewa')},
                'admin_url': reverse('report_barang'),
            },
            {
                'name': 'Laporan Data Pelanggan',
                'object_name': 'laporan_pelanggan',
                'perms': {'view': request.user.has_perm('core.view_pelanggan')},
                'admin_url': reverse('report_pelanggan'),
            },
        ]

        # 2. Buat "Aplikasi" baru untuk Laporan
        reports_app = {
            'name': 'Laporan',
            'app_label': 'reports_custom', 
            'app_url': '',
            'has_module_perms': True,
            'models': report_models,
        }

        # 3. Masukkan Laporan ke dalam daftar aplikasi (app_list)
        # Cari index aplikasi 'core'
        core_index = next((i for i, app in enumerate(app_list) if app['app_label'] == 'core'), -1)
        
        if core_index != -1:
            app_list.insert(core_index + 1, reports_app)
        else:
            app_list.append(reports_app)

        return app_list

# Instansiasi Custom Admin Site
custom_admin_site = CustomAdminSite(name='custom_admin')
# Menimpa variabel admin.site global dengan instance kustom
admin.site = custom_admin_site 


# --- Langkah 3: PENDAFTARAN MODEL KE CUSTOM ADMIN SITE ---

# Daftarkan User dan Group ke Custom Admin Site
custom_admin_site.register(User)
custom_admin_site.register(Group)


# --- Admin Class untuk Pelanggan ---
@admin.register(Pelanggan, site=custom_admin_site)
class PelangganAdmin(admin.ModelAdmin):
    list_display = ('idPelanggan', 'namaPelanggan', 'noHp', 'aksi_link') 
    search_fields = ('namaPelanggan', 'noHp')
    list_filter = ('namaPelanggan',)
    
    def aksi_link(self, obj):
        edit_url = f'/admin/core/pelanggan/{obj.idPelanggan}/change/' 
        edit_icon = f'<a href="{edit_url}" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_url = f'/admin/core/pelanggan/{obj.idPelanggan}/delete/'
        delete_icon = f'<a href="{delete_url}" title="Hapus"><i class="fas fa-trash-alt" style="color: red;"></i></a>'
        return format_html(f'{edit_icon} &nbsp; {delete_icon}')
    aksi_link.short_description = 'Aksi'


# --- Admin Class untuk Barang ---
@admin.register(Barang, site=custom_admin_site)
class BarangAdmin(admin.ModelAdmin):
    list_display = ('idBarang', 'namaBarang', 'harga_formatted', 'stok', 'ukuran', 'foto_preview', 'aksi_link')
    search_fields = ('namaBarang',)
    list_filter = ('ukuran',)
    
    def harga_formatted(self, obj):
        return f"Rp {intcomma(obj.harga)}"
    harga_formatted.short_description = 'Harga'
    harga_formatted.admin_order_field = 'harga'
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.foto.url)
        return "No Image"
    foto_preview.short_description = 'Foto'
    
    def aksi_link(self, obj):
        edit_url = f'/admin/core/barang/{obj.idBarang}/change/' 
        edit_icon = f'<a href="{edit_url}" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_url = f'/admin/core/barang/{obj.idBarang}/delete/'
        delete_icon = f'<a href="{delete_url}" title="Hapus"><i class="fas fa-trash-alt" style="color: red;"></i></a>'
        return format_html(f'{edit_icon} &nbsp; {delete_icon}')
    aksi_link.short_description = 'Aksi'


# --- Inline dan Admin Class untuk Penyewaan ---
class DetailSewaInline(admin.TabularInline):
    model = DetailSewa
    fields = ('idBarang', 'jumlahBarang', 'jumlahBermasalah', 'statusBarang', 'subTotal')
    readonly_fields = ('subTotal',) 
    extra = 1

    
@admin.register(Penyewaan, site=custom_admin_site)
class PenyewaanAdmin(admin.ModelAdmin):
    inlines = [DetailSewaInline]
    list_display = (
         'idPenyewaan', 'tanggalPesan', 'tanggalAcara', 'durasiSewa', 'total_bayar_formatted', 'statusSewa', 'idPelanggan', 'aksi_link'
    )
    search_fields = ('idPelanggan__namaPelanggan', 'statusSewa')
    list_filter = ('statusSewa', 'tanggalAcara')
    
    fieldsets = (
        (None, {
            'fields': ('idPelanggan', 'tanggalAcara', 'tanggalPembongkaran', 'durasiSewa', 'alamatPemasangan')
        }),
        ('Detail Pembayaran dan Status', {
            'fields': ('totalBayar', 'statusSewa', 'feedback'), 
            'classes': ('collapse',),
        })
    )
    readonly_fields = ('totalBayar', 'tanggalPesan')
    
    def total_bayar_formatted(self, obj):
        if obj.totalBayar:
            return f"Rp {intcomma(obj.totalBayar)}"
        return "Rp 0"
    total_bayar_formatted.short_description = 'Total Bayar'
    total_bayar_formatted.admin_order_field = 'totalBayar'
    
    def calculate_total_bayar(self, penyewaan_instance):
        total_sum = penyewaan_instance.detailsewa_set.aggregate(
            total=Sum(F('subTotal'))
        )['total']
        
        if total_sum is not None:
            penyewaan_instance.totalBayar = total_sum
            penyewaan_instance.save(update_fields=['totalBayar'])

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        if change:
            self.calculate_total_bayar(obj)
            
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, DetailSewa):
                # Update statusBarang based on jumlahBermasalah
                if instance.jumlahBermasalah > 0 and instance.statusBarang == 'Baik':
                    # Default to 'Rusak' if there are issues
                    instance.statusBarang = 'Rusak'
                elif instance.jumlahBermasalah == 0 and instance.statusBarang in ['Rusak', 'Hilang']:
                    # Reset to 'Baik' if no issues
                    instance.statusBarang = 'Baik'
                instance.save() 
        
        formset.save_m2m()
        
        for obj in formset.deleted_objects:
            obj.delete()

        if form.instance.pk:
            self.calculate_total_bayar(form.instance)
            
    def aksi_link(self, obj):
        edit_url = f'/admin/core/penyewaan/{obj.idPenyewaan}/change/' 
        edit_icon = f'<a href="{edit_url}" title="Edit"><i class="fas fa-edit"></i></a>'
        delete_url = f'/admin/core/penyewaan/{obj.idPenyewaan}/delete/'
        delete_icon = f'<a href="{delete_url}" title="Hapus"><i class="fas fa-trash-alt" style="color: red;"></i></a>'
        return format_html(f'{edit_icon} &nbsp; {delete_icon}')
    aksi_link.short_description = 'Aksi'