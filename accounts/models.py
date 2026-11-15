from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'مدیریت کل'),
        ('admin', 'مدیریت سایت'),
        ('agency', 'آژانس املاک'),
        ('user', 'کاربر عادی'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # فیلدهای مربوط به آژانس (فقط برای نقش agency پر می‌شود)
    agency_name = models.CharField(max_length=100, blank=True, null=True)
    agency_address = models.CharField(max_length=255, blank=True, null=True)
    agency_phone = models.CharField(max_length=15, blank=True, null=True)
    agency_logo = models.ImageField(upload_to='agencies/logos/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

    @property
    def has_active_license(self):
        """آیا این کاربر (آژانس) لایسنس فعال دارد؟"""
        if self.role not in ('agency', 'admin', 'superadmin'):
            return False
        license_obj = getattr(self, 'license_info', None)
        if not license_obj:
            return False
        return license_obj.is_active and license_obj.expires_at > timezone.now()

    @property
    def can_post_property(self):
        """آیا اجازه ثبت آگهی دارد؟"""
        if self.role in ('superadmin', 'admin'):
            return True
        if self.role == 'agency':
            return self.has_active_license
        return False


class License(models.Model):
    STATUS_CHOICES = (
        ('active', 'فعال'),
        ('expired', 'منقضی شده'),
        ('pending', 'در انتظار تایید'),
        ('rejected', 'رد شده'),
    )
    agency = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='license_info'
    )
    license_key = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'لایسنس آژانس'
        verbose_name_plural = 'لایسنس‌های آژانس‌ها'

    def __str__(self):
        return f"{self.agency.username} - {self.license_key[:8]}..."

    def is_valid(self):
        return self.is_active and self.status == 'active' and self.expires_at > timezone.now()