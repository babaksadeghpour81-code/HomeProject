from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden

from .models import (
    ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty
)
from .forms import (
    ResidentialPropertyForm, IndustrialPropertyForm,
    LandPropertyForm, GardenPropertyForm
)


def home(request):
    """صفحه اصلی"""
    latest = []
    for Model in [ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty]:
        latest += list(Model.objects.filter(is_active=True)[:3])
    latest.sort(key=lambda x: x.created_at, reverse=True)
    return render(request, 'home.html', {'latest_properties': latest[:9]})


def property_list(request):
    """لیست آگهی‌ها با فیلتر status"""
    status = request.GET.get('status', '')
    property_type = request.GET.get('type', '')

    all_props = []
    models_map = {
        'villa': ResidentialProperty,
        'apartment': ResidentialProperty,
        'commercial': ResidentialProperty,
        'office': ResidentialProperty,
        'industrial': IndustrialProperty,
        'land': LandProperty,
        'garden': GardenProperty,
    }

    # اگر نوع مشخص شده، فقط همان مدل را جستجو کن
    if property_type and property_type in models_map:
        Model = models_map[property_type]
        qs = Model.objects.filter(is_active=True)
        if property_type in ('villa', 'apartment', 'commercial', 'office'):
            qs = qs.filter(property_type=property_type)
        if status:
            qs = qs.filter(status=status)
        all_props = list(qs)
    else:
        # همه مدل‌ها
        for Model in [ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty]:
            qs = Model.objects.filter(is_active=True)
            if status:
                qs = qs.filter(status=status)
            all_props += list(qs)

    all_props.sort(key=lambda x: x.created_at, reverse=True)
    return render(request, 'properties/property_list.html', {
        'properties': all_props,
        'current_status': status,
        'current_type': property_type,
    })


def property_detail(request, pk, property_type):
    """جزئیات آگهی"""
    model_map = {
        'residential': ResidentialProperty,
        'industrial': IndustrialProperty,
        'land': LandProperty,
        'garden': GardenProperty,
    }
    Model = model_map.get(property_type)
    if not Model:
        messages.error(request, 'نوع ملک یافت نشد.')
        return redirect('properties:property_list')
    prop = get_object_or_404(Model, pk=pk)
    return render(request, 'properties/property_detail.html', {'prop': prop})


@login_required
def property_create(request):
    """ثبت آگهی - چک لایسنس"""
    if not request.user.can_post_property:
        messages.error(request, 'برای ثبت آگهی باید لایسنس فعال داشته باشید.')
        return redirect('properties:home')

    if request.method == 'POST':
        # تشخیص نوع ملک از فیلد hidden یا انتخاب کاربر
        property_type = request.POST.get('property_type')
        status = request.POST.get('status')

        form_class = None
        if property_type in ('villa', 'apartment', 'commercial', 'office'):
            form_class = ResidentialPropertyForm
        elif property_type == 'industrial':
            form_class = IndustrialPropertyForm
        elif property_type == 'land':
            form_class = LandPropertyForm
        elif property_type == 'garden':
            form_class = GardenPropertyForm

        if form_class:
            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                prop = form.save(commit=False)
                prop.owner = request.user
                prop.property_type = property_type
                prop.status = status
                prop.save()
                messages.success(request, 'آگهی با موفقیت ثبت شد.')
                return redirect('properties:property_list')
            else:
                messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید.')
        else:
            messages.error(request, 'نوع ملک نامعتبر است.')

    return render(request, 'properties/property_form.html', {
        'property_types': [
            ('villa', 'ویلایی'), ('apartment', 'آپارتمان'),
            ('commercial', 'تجاری'), ('office', 'اداری'),
            ('industrial', 'صنعتی'), ('land', 'زمین'), ('garden', 'باغ'),
        ],
        'status_choices': ResidentialProperty.STATUS_CHOICES,
    })