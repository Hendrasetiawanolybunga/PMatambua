from django.contrib.auth.backends import BaseBackend
from .models import Pelanggan

class PelangganAuthBackend(BaseBackend):
    def authenticate(self, request, noHp=None, password=None):
        try:
            pelanggan = Pelanggan.objects.get(noHp=noHp)
            if pelanggan.check_password(password):
                return pelanggan
        except Pelanggan.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return Pelanggan.objects.get(pk=user_id)
        except Pelanggan.DoesNotExist:
            return None