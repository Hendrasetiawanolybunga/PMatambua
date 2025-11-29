
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import instance custom_admin_site dari core.admin
from core.admin import custom_admin_site 

urlpatterns = [
    # Ganti 'admin.site.urls' dengan custom_admin_site.urls
    path('admin/', custom_admin_site.urls), 
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)