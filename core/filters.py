# core/filters.py
import django_filters
from .models import Penyewaan, DetailSewa, Pelanggan
from django import forms

class PenyewaanFilter(django_filters.FilterSet):
    # Filter Status
    statusSewa = django_filters.ChoiceFilter(
        choices=Penyewaan.statusSewa.field.choices,
        empty_label="Semua Status",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Filter Rentang Tanggal Pesan
    tanggalPesan__gte = django_filters.DateFilter(
        field_name='tanggalPesan', 
        lookup_expr='gte', 
        label='Dari Tanggal',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    tanggalPesan__lte = django_filters.DateFilter(
        field_name='tanggalPesan', 
        lookup_expr='lte', 
        label='Sampai Tanggal',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Penyewaan
        fields = ['statusSewa', 'tanggalPesan__gte', 'tanggalPesan__lte']


class KeuanganFilter(django_filters.FilterSet):
    # Keuangan hanya menghitung Penyewaan yang statusnya Completed atau Confirmed
    # Filter Rentang Tanggal Pesan
    tanggalPesan__gte = django_filters.DateFilter(
        field_name='tanggalPesan', 
        lookup_expr='gte', 
        label='Dari Tanggal',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    tanggalPesan__lte = django_filters.DateFilter(
        field_name='tanggalPesan', 
        lookup_expr='lte', 
        label='Sampai Tanggal',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Penyewaan
        fields = ['tanggalPesan__gte', 'tanggalPesan__lte']


class DetailBarangFilter(django_filters.FilterSet):
    # Filter Status Barang (Baik, Rusak, Hilang)
    statusBarang = django_filters.ChoiceFilter(
        choices=DetailSewa.statusBarang.field.choices,
        empty_label="Semua Status Barang",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = DetailSewa
        fields = ['statusBarang']