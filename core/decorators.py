from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def pelanggan_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if pelanggan is in session
        if 'pelanggan_id' not in request.session:
            messages.error(request, 'Anda harus login terlebih dahulu.')
            return redirect('login_pelanggan')
        
        # Check if pelanggan exists in database
        try:
            from .models import Pelanggan
            pelanggan = Pelanggan.objects.get(idPelanggan=request.session['pelanggan_id'])
        except Pelanggan.DoesNotExist:
            # Remove invalid session
            if 'pelanggan_id' in request.session:
                del request.session['pelanggan_id']
            messages.error(request, 'Sesi anda tidak valid. Silakan login kembali.')
            return redirect('login_pelanggan')
            
        return view_func(request, *args, **kwargs)
    return wrapper