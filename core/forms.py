from django import forms
from .models import Pelanggan

class PelangganRegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan password'})
    )
    password2 = forms.CharField(
        label='Konfirmasi Password', 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Konfirmasi password'})
    )

    class Meta:
        model = Pelanggan
        fields = ('namaPelanggan', 'noHp')
        widgets = {
            'namaPelanggan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Lengkap'}),
            'noHp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor HP'}),
        }

    def clean_noHp(self):
        noHp = self.cleaned_data.get('noHp')
        if Pelanggan.objects.filter(noHp=noHp).exists():
            raise forms.ValidationError("Nomor HP ini sudah terdaftar.")
        return noHp

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password tidak cocok")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        pelanggan = super().save(commit=False)
        pelanggan.set_password(self.cleaned_data["password1"])
        if commit:
            pelanggan.save()
        return pelanggan

class PelangganLoginForm(forms.Form):
    noHp = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor HP'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        noHp = cleaned_data.get('noHp')
        password = cleaned_data.get('password')

        if noHp and password:
            try:
                pelanggan = Pelanggan.objects.get(noHp=noHp)
                if not pelanggan.check_password(password):
                    raise forms.ValidationError("Nomor HP atau password salah.")
            except Pelanggan.DoesNotExist:
                raise forms.ValidationError("Nomor HP atau password salah.")
        
        return cleaned_data