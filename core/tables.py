# core/tables.py
import django_tables2 as tables
from .models import Penyewaan, DetailSewa, Barang, Pelanggan
from django_tables2.utils import A
from django.utils.safestring import mark_safe

class PenyewaanReportTable(tables.Table):
    # Field untuk menampilkan link ke detail penyewaan (opsional)
    idPenyewaan = tables.Column(verbose_name="ID Sewa")
    pelanggan = tables.Column(accessor=A('idPelanggan.namaPelanggan'), verbose_name="Nama Pelanggan")
    tanggalPesan = tables.DateColumn(verbose_name="Tgl Pesan", format="d/m/Y")
    statusSewa = tables.Column(verbose_name="Status")
    totalBayar = tables.Column(verbose_name="Total Bayar")

    class Meta:
        model = Penyewaan
        template_name = "django_tables2/bootstrap4.html"
        fields = ('idPenyewaan', 'pelanggan', 'tanggalPesan', 'tanggalAcara', 'durasiSewa', 'statusSewa', 'totalBayar')
        attrs = {"class": "table table-bordered table-striped"}

class KeuanganReportTable(tables.Table):
    tanggalPesan = tables.DateColumn(verbose_name="Tanggal", format="d/m/Y")
    idPenyewaan = tables.Column(verbose_name="ID Sewa")
    pelanggan = tables.Column(accessor=A('idPelanggan.namaPelanggan'), verbose_name="Pelanggan")
    statusSewa = tables.Column(verbose_name="Status")
    totalBayar = tables.Column(verbose_name="Pendapatan (Rp)")
    
    class Meta:
        model = Penyewaan
        template_name = "django_tables2/bootstrap4.html"
        fields = ('tanggalPesan', 'idPenyewaan', 'pelanggan', 'statusSewa', 'totalBayar')
        attrs = {"class": "table table-bordered table-striped"}

class BarangReportTable(tables.Table):
    namaBarang = tables.Column(verbose_name="Nama Barang")
    ukuran = tables.Column(verbose_name="Ukuran")
    stok = tables.Column(verbose_name="Stok Saat Ini")
    
    class Meta:
        model = Barang
        template_name = "django_tables2/bootstrap4.html"
        fields = ('idBarang', 'namaBarang', 'ukuran', 'stok', 'harga')
        attrs = {"class": "table table-bordered table-striped"}

class DetailBarangReportTable(tables.Table):
    # Mengambil data dari DetailSewa
    idPenyewaan = tables.Column(accessor=A('idPenyewaan.idPenyewaan'), verbose_name="ID Sewa")
    tanggalAcara = tables.DateColumn(accessor=A('idPenyewaan.tanggalAcara'), verbose_name="Tgl Acara", format="d/m/Y")
    namaBarang = tables.Column(accessor=A('idBarang.namaBarang'), verbose_name="Barang")
    jumlahBarang = tables.Column(verbose_name="Jumlah")
    statusBarang = tables.Column(verbose_name="Status Barang")

    class Meta:
        model = DetailSewa
        template_name = "django_tables2/bootstrap4.html"
        fields = ('idPenyewaan', 'tanggalAcara', 'namaBarang', 'jumlahBarang', 'statusBarang')
        attrs = {"class": "table table-bordered table-striped"}

class PelangganReportTable(tables.Table):
    idPelanggan = tables.Column(verbose_name="ID Pelanggan")
    namaPelanggan = tables.Column(verbose_name="Nama Pelanggan")
    noHp = tables.Column(verbose_name="No. HP")
    
    class Meta:
        model = Pelanggan
        template_name = "django_tables2/bootstrap4.html"
        fields = ('idPelanggan', 'namaPelanggan', 'noHp')
        attrs = {"class": "table table-bordered table-striped"}