from django.db import models
from django.conf import settings
from django_jalali.db import models as jmodels


class LoanRequest(models.Model):
    LOAN_TYPE_CHOICES = (
        ('purchase', 'خرید ملک'),
        ('construction', 'ساخت'),
        ('renovation', 'بازسازی'),
    )
    STATUS_CHOICES = (
        ('pending', 'در انتظار بررسی'),
        ('reviewing', 'در حال بررسی'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='loan_requests'
    )
    full_name = models.CharField(max_length=100, verbose_name='نام و نام خانوادگی')
    national_code = models.CharField(max_length=10, verbose_name='کد ملی')
    phone = models.CharField(max_length=15, verbose_name='شماره تماس')
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES, verbose_name='نوع وام')
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='مبلغ درخواستی')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    created_at = jmodels.jDateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'درخواست وام'
        verbose_name_plural = 'درخواست‌های وام'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.get_loan_type_display()}"