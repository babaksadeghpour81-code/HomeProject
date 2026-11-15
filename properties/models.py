from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_jalali.db import models as jmodels


class BaseProperty(models.Model):
    STATUS_CHOICES = (
        ('sale', 'خرید و فروش'),
        ('rent', 'رهن و اجاره'),
        ('barter', 'تهاتر'),
        ('business', 'فایل کاسبی'),
        ('garden', 'باغ و باغچه'),
    )
    PROPERTY_TYPE_CHOICES = (
        ('villa', 'ویلایی'),
        ('apartment', 'آپارتمان'),
        ('commercial', 'تجاری'),
        ('office', 'اداری'),
        ('industrial', 'صنعتی'),
        ('land', 'زمین'),
        ('garden', 'باغ'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties',
        verbose_name='آگهی‌دهنده'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='نوع آگهی')
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE_CHOICES,
        verbose_name='نوع ملک'
    )
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیحات')

    # قیمت‌ها (برای فروش از price، برای رهن/اجاره از deposit و rent استفاده می‌شود)
    price = models.DecimalField(
        max_digits=15, decimal_places=0,
        blank=True, null=True,
        verbose_name='قیمت کل (فروش)'
    )
    deposit = models.DecimalField(
        max_digits=15, decimal_places=0,
        blank=True, null=True,
        verbose_name='ودیعه (رهن)'
    )
    rent = models.DecimalField(
        max_digits=15, decimal_places=0,
        blank=True, null=True,
        verbose_name='اجاره ماهیانه'
    )

    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='زمان انتشار')
    updated_at = jmodels.jDateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    # فایل‌های چندرسانه‌ای
    video_url = models.URLField(blank=True, null=True, verbose_name='لینک ویدیو (اختیاری)')
    video_file = models.FileField(
        upload_to='properties/videos/', blank=True, null=True,
        verbose_name='فایل ویدیو (اختیاری)'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_property_type_display()}"


class ResidentialProperty(BaseProperty):
    """ویلایی، آپارتمان، تجاری، اداری"""
    LOCATION_CHOICES = (
        ('phase1', 'فاز یک'), ('phase2', 'فاز دو'), ('phase3', 'فاز سه'),
        ('phase4', 'فاز چهار'), ('phase5', 'فاز پنج'), ('phase6', 'فاز شش'),
        ('other', 'سایر'),
    )
    location_phase = models.CharField(
        max_length=20, choices=LOCATION_CHOICES, default='other',
        verbose_name='لوکیشن (فاز)'
    )
    location_text = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name='لوکیشن (توضیح)'
    )
    area = models.PositiveIntegerField(verbose_name='متراژ')
    bedrooms = models.PositiveIntegerField(default=0, verbose_name='تعداد خواب')
    floor = models.IntegerField(default=0, verbose_name='طبقه')
    total_floors = models.PositiveIntegerField(default=0, verbose_name='تعداد کل طبقات')
    units_per_floor = models.PositiveIntegerField(default=0, verbose_name='واحد در هر طبقه')
    building_age = models.PositiveIntegerField(default=0, verbose_name='سن بنا')
    has_elevator = models.BooleanField(default=False, verbose_name='آسانسور')
    has_storage = models.BooleanField(default=False, verbose_name='انباری')
    has_parking = models.BooleanField(default=False, verbose_name='پارکینگ')
    has_balcony = models.BooleanField(default=False, verbose_name='بالکن/تراس')
    amenities = models.TextField(blank=True, null=True, verbose_name='امکانات')

    def clean(self):
        # اعتبارسنجی: اگر status = sale، price باید پر باشد؛ اگر rent، deposit/rent پر باشد
        from django.core.exceptions import ValidationError
        if self.status == 'sale' and not self.price:
            raise ValidationError('برای فروش، قیمت الزامی است.')
        if self.status == 'rent' and not (self.deposit or self.rent):
            raise ValidationError('برای رهن/اجاره، ودیعه یا اجاره ماهیانه الزامی است.')

    class Meta:
        verbose_name = 'ملک مسکونی/تجاری/اداری'
        verbose_name_plural = 'املاک مسکونی/تجاری/اداری'


class IndustrialProperty(BaseProperty):
    """صنعتی"""
    usage = models.CharField(max_length=100, verbose_name='کاربری')
    area = models.PositiveIntegerField(verbose_name='متراژ')

    class Meta:
        verbose_name = 'ملک صنعتی'
        verbose_name_plural = 'املاک صنعتی'


class LandProperty(BaseProperty):
    """زمین"""
    usage = models.CharField(max_length=100, verbose_name='کاربری')
    area = models.PositiveIntegerField(verbose_name='متراژ')

    class Meta:
        verbose_name = 'زمین'
        verbose_name_plural = 'زمین‌ها'


class GardenProperty(BaseProperty):
    """باغ و ویلا"""
    area = models.PositiveIntegerField(verbose_name='متراژ')

    class Meta:
        verbose_name = 'باغ و ویلا'
        verbose_name_plural = 'باغ‌ها و ویلاها'


class PropertyImage(models.Model):
    """عکس‌های آگهی (متصل به هر مدل آگهی از طریق GenericForeignKey)"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    image = models.ImageField(upload_to='properties/images/', verbose_name='عکس')
    caption = models.CharField(max_length=200, blank=True, null=True, verbose_name='توضیح عکس')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'عکس آگهی'
        verbose_name_plural = 'عکس‌های آگهی'
        ordering = ['order']

    def __str__(self):
        return f"عکس {self.id} - {self.content_type}"