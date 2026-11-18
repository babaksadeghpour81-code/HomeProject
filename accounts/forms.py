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
    first_name = forms.CharField(
        label='نام',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'})
    )
    last_name = forms.CharField(
        label='نام خانوادگی',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'})
    )
    national_card_image = forms.ImageField(
        label='عکس کارت ملی',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    business_license_image = forms.ImageField(
        label='عکس جواز کسب (اختیاری)',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'phone_number',
            'agency_name', 'agency_address', 'agency_phone',
            'national_card_image', 'business_license_image',
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'کد ملی ۱۰ رقمی',
                'maxlength': '10', 'inputmode': 'numeric',
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '09123456789',
                'inputmode': 'numeric',
            }),
            'agency_name': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_address': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        username = username.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))
        if not username.isdigit() or len(username) != 10:
            raise forms.ValidationError('کد ملی باید ۱۰ رقم عددی باشد.')
        return username

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        phone = phone.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))
        if not phone:
            raise forms.ValidationError('شماره موبایل الزامی است.')
        if not phone.isdigit() or len(phone) != 11 or not phone.startswith('09'):
            raise forms.ValidationError('شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود.')
        return phone

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('رمز عبور و تکرار آن یکسان نیستند.')
        if p1 and len(p1) < 8:
            raise forms.ValidationError('رمز عبور باید حداقل ۸ کاراکتر باشد.')
        return p2

    # ✅ اعتبارسنجی عکس‌ها در clean_* (نه در save)
    def clean_national_card_image(self):
        img = self.cleaned_data.get('national_card_image')
        if img and img.size > 5 * 1024 * 1024:
            raise forms.ValidationError('حجم عکس کارت ملی نباید بیشتر از ۵ مگابایت باشد.')
        return img

    def clean_business_license_image(self):
        img = self.cleaned_data.get('business_license_image')
        if img and img.size > 5 * 1024 * 1024:
            raise forms.ValidationError('حجم عکس جواز کسب نباید بیشتر از ۵ مگابایت باشد.')
        return img

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.role = 'agency'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if self.cleaned_data.get('national_card_image'):
            user.national_card_image = self.cleaned_data['national_card_image']
        if self.cleaned_data.get('business_license_image'):
            user.business_license_image = self.cleaned_data['business_license_image']

        if commit:
            user.save()
        return user


class AgencyProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'agency_name',
            'agency_address',
            'agency_phone',
            'agency_logo',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '09123456789',
                'inputmode': 'numeric',
            }),
            'agency_name': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_address': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'agency_logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
            'phone_number': 'شماره موبایل',
            'agency_name': 'نام آژانس',
            'agency_address': 'آدرس آژانس',
            'agency_phone': 'تلفن آژانس',
            'agency_logo': 'لوگوی آژانس',
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        phone = phone.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))
        if not phone:
            raise forms.ValidationError('شماره موبایل الزامی است.')
        if not phone.isdigit() or len(phone) != 11 or not phone.startswith('09'):
            raise forms.ValidationError('شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود.')
        return phone

# ============================================================
# فرم‌های تغییر/بازنشانی رمز عبور
# ============================================================

class PasswordChangeForm(forms.Form):
    """تغییر رمز عبور توسط کاربر لاگین‌شده"""
    current_password = forms.CharField(
        label='رمز عبور فعلی',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='تکرار رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        pwd = self.cleaned_data.get('current_password')
        if not self.user.check_password(pwd):
            raise forms.ValidationError('رمز عبور فعلی اشتباه است.')
        return pwd

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError('رمز عبور جدید و تکرار آن یکسان نیستند.')
            if len(p1) < 8:
                raise forms.ValidationError('رمز عبور جدید باید حداقل ۸ کاراکتر باشد.')
        return cleaned


class PasswordResetRequestForm(forms.Form):
    """فرم درخواست بازنشانی رمز - دریافت کد ملی"""
    national_code = forms.CharField(
        label='کد ملی',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد ملی ۱۰ رقمی',
            'inputmode': 'numeric',
            'maxlength': '10',
        })
    )

    def clean_national_code(self):
        code = self.cleaned_data['national_code'].strip()
        code = code.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))
        if not code.isdigit() or len(code) != 10:
            raise forms.ValidationError('کد ملی باید ۱۰ رقم عددی باشد.')
        return code


class PasswordResetVerifyForm(forms.Form):
    """فرم تایید OTP و تغییر رمز"""
    otp_code = forms.CharField(
        label='کد تایید',
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد ۶ رقمی پیامک شده',
            'inputmode': 'numeric',
            'maxlength': '6',
        })
    )
    new_password1 = forms.CharField(
        label='رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='تکرار رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean_otp_code(self):
        code = self.cleaned_data['otp_code'].strip()
        code = code.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError('کد تایید باید ۶ رقم عددی باشد.')
        return code

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError('رمز عبور و تکرار آن یکسان نیستند.')
            if len(p1) < 8:
                raise forms.ValidationError('رمز عبور باید حداقل ۸ کاراکتر باشد.')
        return cleaned

