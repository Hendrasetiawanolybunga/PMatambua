from django.db import models
from django.db.models import F

class Pelanggan(models.Model):
    idPelanggan = models.AutoField(primary_key=True)
    namaPelanggan = models.CharField(max_length=50)
    noHp = models.CharField(max_length=15)
    
    class Meta:
        verbose_name = "Pelanggan"
        verbose_name_plural = "Pelanggan"
    
    def __str__(self):
        return self.namaPelanggan
    

class Barang(models.Model):
    idBarang = models.AutoField(primary_key=True)
    namaBarang = models.CharField(max_length=50)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    stok = models.PositiveIntegerField()
    deskripsi = models.CharField(max_length=200)
    ukuran = models.CharField(max_length=30)
    foto = models.ImageField(upload_to='foto_barang/',blank=True,null=True,verbose_name="Foto Produk")

    class Meta:
        verbose_name = "Barang"
        verbose_name_plural = "Barang"
    
    def __str__(self):
        return self.namaBarang
    
class Penyewaan(models.Model):
    idPenyewaan = models.AutoField(primary_key=True)
    tanggalPesan = models.DateField(auto_now_add=True)
    tanggalAcara = models.DateField()
    durasiSewa = models.PositiveIntegerField()
    # Null=True dan blank=True agar bisa diisi otomatis di Admin
    totalBayar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    statusSewa = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ])
    feedback = models.TextField(blank=True, null=True)
    alamatPemasangan = models.CharField(max_length=200)
    tanggalPembongkaran = models.DateField()
    idPelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Penyewaan"
        verbose_name_plural = "Penyewaan"
    
    def __str__(self):
        return f'Sewa {self.idPenyewaan} oleh {self.idPelanggan.namaPelanggan}'
    
class DetailSewa(models.Model):
    idDetailSewa = models.AutoField(primary_key=True)
    idPenyewaan = models.ForeignKey(Penyewaan, on_delete=models.CASCADE)
    idBarang = models.ForeignKey(Barang, on_delete=models.CASCADE)
    jumlahBarang = models.PositiveIntegerField()
    statusBarang = models.CharField(max_length=20, choices=[
        ('Baik', 'Baik'),
        ('Rusak', 'Rusak'),
        ('Hilang', 'Hilang'),
    ], default='Baik')
    # Null=True dan blank=True agar bisa dihitung otomatis di Admin
    subTotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Pastikan idBarang tersedia sebelum melakukan operasi stok
        if not self.idBarang:
            super().save(*args, **kwargs)
            return

        # --- Logika Penyesuaian Stok ---
        if self.pk:
            # Kasus Update/Edit
            # Ambil objek lama untuk mengetahui jumlah barang sebelumnya
            original_detail = DetailSewa.objects.get(pk=self.pk)
            old_jumlah = original_detail.jumlahBarang
            
            # Hitung perubahan stok: Stok harus berkurang sebesar (jumlahBarang baru - jumlahBarang lama)
            # Contoh: Dari 5 menjadi 8. Perubahan = 3 (stok berkurang 3). 
            # Contoh: Dari 8 menjadi 5. Perubahan = -3 (stok bertambah 3).
            stok_adjustment = old_jumlah - self.jumlahBarang
        else:
            # Kasus Create/Baru
            # Stok berkurang sebesar jumlahBarang yang baru
            stok_adjustment = -self.jumlahBarang
        
        # --- Logika SubTotal ---
        if self.idBarang and self.jumlahBarang is not None:
            self.subTotal = self.idBarang.harga * self.jumlahBarang

        # Simpan DetailSewa
        super().save(*args, **kwargs)

        # --- Update Stok Barang secara Atomik ---
        # Menggunakan F() expression untuk menghindari race condition
        Barang.objects.filter(pk=self.idBarang.pk).update(stok=F('stok') + stok_adjustment)

    def delete(self, *args, **kwargs):
        # --- Logika Pengembalian Stok saat DetailSewa dihapus ---
        barang = self.idBarang
        # Kembalikan jumlah barang yang disewa ke stok
        Barang.objects.filter(pk=barang.pk).update(stok=F('stok') + self.jumlahBarang)
        
        # Hapus DetailSewa
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Detail Sewa"
        verbose_name_plural = "Detail Sewa"

    def __str__(self):
        return f'Detail Sewa {self.idDetailSewa} untuk Sewa {self.idPenyewaan.idPenyewaan}'