from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'agency_name', 'agency_address', 'agency_phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_name': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_address': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('رمز عبور و تکرار آن یکسان نیستند.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.role = 'agency'  # پیش‌فرض: آژانس املاک
        if commit:
            user.save()
        return user


# ============================================================
# فرم ویرایش پروفایل آژانس (اضافه شد)
# ============================================================

class AgencyProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'agency_name',
            'agency_address',
            'agency_phone',
            'phone_number',
            'email',
            'agency_logo',
        ]
        widgets = {
            'agency_name': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_address': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'agency_logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'agency_name': 'نام آژانس',
            'agency_address': 'آدرس آژانس',
            'agency_phone': 'تلفن آژانس',
            'phone_number': 'شماره تماس شخصی',
            'email': 'ایمیل',
            'agency_logo': 'لوگوی آژانس',
        }