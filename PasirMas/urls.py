# project_name/urls.py

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Import instance custom_admin_site dari core.admin
from core.admin import custom_admin_site 
# Import URL laporan
from core.urls import report_urls 

urlpatterns = [
    # ----------------------------------------------------------------------
    # 1. INJEKSI URL KUSTOM (LAPORAN) KE NAMESPACE 'admin'
    # Perintah 'include(report_urls)' akan mencocokkan URL yang namanya 
    # digunakan di JAZZMIN_SETTINGS (contoh: 'admin:report_penyewaan').
    # ----------------------------------------------------------------------
    path('admin/', include(report_urls)), 
    
    # ----------------------------------------------------------------------
    # 2. URL ADMIN KUSTOM
    # Ini harus berada di baris kedua. Jika diletakkan di baris pertama, 
    # ia akan menelan semua permintaan ke /admin/ termasuk yang seharusnya 
    # ditangani oleh report_urls.
    # ----------------------------------------------------------------------
    path('admin/', custom_admin_site.urls), 
    
    # Contoh: Redirect dari root ke admin
    path('', RedirectView.as_view(url='admin/', permanent=True)),
]

# Menambahkan URL untuk file media dan statis hanya saat mode DEBUG aktif
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Tambahkan juga static files untuk berjaga-jaga (meskipun biasanya ditangani server)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)