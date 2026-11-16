from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import ConstructionProject
from .forms import ConstructionProjectForm
from django.core.paginator import Paginator
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
    """لیست آگهی‌ها با فیلتر پیشرفته"""
    status = request.GET.get('status', '')
    property_type = request.GET.get('type', '')
    min_area = request.GET.get('min_area', '')
    max_area = request.GET.get('max_area', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    bedrooms = request.GET.get('bedrooms', '')
    location_phase = request.GET.get('location_phase', '')
    sort = request.GET.get('sort', '-created_at')

    # تبدیل امن به عدد
    def to_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    min_area_val = to_int(min_area)
    max_area_val = to_int(max_area)
    min_price_val = to_int(min_price)
    max_price_val = to_int(max_price)
    bedrooms_val = to_int(bedrooms)

    # آیا فیلتر مخصوص residential فعال است؟
    residential_only_filter = bool(bedrooms_val or location_phase)

    models_map = {
        'villa': ResidentialProperty,
        'apartment': ResidentialProperty,
        'commercial': ResidentialProperty,
        'office': ResidentialProperty,
        'industrial': IndustrialProperty,
        'land': LandProperty,
        'garden': GardenProperty,
    }

    # تعریف همه مدل‌ها با کلید
    all_models = [
        ('residential', ResidentialProperty),
        ('industrial', IndustrialProperty),
        ('land', LandProperty),
        ('garden', GardenProperty),
    ]

    all_props = []

    # اگر نوع مشخص شده
    if property_type and property_type in models_map:
        Model = models_map[property_type]
        qs = Model.objects.filter(is_active=True)

        # فیلتر property_type (فقط برای residential)
        if property_type in ('villa', 'apartment', 'commercial', 'office'):
            qs = qs.filter(property_type=property_type)

        # فیلترهای عمومی
        if status:
            qs = qs.filter(status=status)
        if min_area_val is not None:
            qs = qs.filter(area__gte=min_area_val)
        if max_area_val is not None:
            qs = qs.filter(area__lte=max_area_val)
        if min_price_val is not None:
            qs = qs.filter(price__gte=min_price_val)
        if max_price_val is not None:
            qs = qs.filter(price__lte=max_price_val)

        # فیلترهای مخصوص residential
        if property_type in ('villa', 'apartment', 'commercial', 'office'):
            if bedrooms_val is not None:
                qs = qs.filter(bedrooms__gte=bedrooms_val)
            if location_phase:
                qs = qs.filter(location_phase=location_phase)

        all_props = list(qs)
    else:
        # همه مدل‌ها
        for key, Model in all_models:
            # اگر فیلتر مخصوص residential فعال است، مدل‌های غیر residential را نادیده بگیر
            if residential_only_filter and key != 'residential':
                continue

            qs = Model.objects.filter(is_active=True)

            # فیلترهای عمومی
            if status:
                qs = qs.filter(status=status)
            if min_area_val is not None:
                qs = qs.filter(area__gte=min_area_val)
            if max_area_val is not None:
                qs = qs.filter(area__lte=max_area_val)
            if min_price_val is not None:
                qs = qs.filter(price__gte=min_price_val)
            if max_price_val is not None:
                qs = qs.filter(price__lte=max_price_val)

            # فیلترهای مخصوص residential
            if key == 'residential':
                if bedrooms_val is not None:
                    qs = qs.filter(bedrooms__gte=bedrooms_val)
                if location_phase:
                    qs = qs.filter(location_phase=location_phase)

            all_props += list(qs)

    # مرتب‌سازی
    if sort == 'price_asc':
        all_props.sort(key=lambda x: float(x.price) if x.price else 0)
    elif sort == 'price_desc':
        all_props.sort(key=lambda x: float(x.price) if x.price else 0, reverse=True)
    elif sort == 'area_asc':
        all_props.sort(key=lambda x: x.area or 0)
    elif sort == 'area_desc':
        all_props.sort(key=lambda x: x.area or 0, reverse=True)
    else:
        all_props.sort(key=lambda x: x.created_at, reverse=True)

    # ===== مرتب‌سازی =====
    if sort == 'price_asc':
        all_props.sort(key=lambda x: float(x.price) if x.price else 0)
    elif sort == 'price_desc':
        all_props.sort(key=lambda x: float(x.price) if x.price else 0, reverse=True)
    elif sort == 'area_asc':
        all_props.sort(key=lambda x: x.area or 0)
    elif sort == 'area_desc':
        all_props.sort(key=lambda x: x.area or 0, reverse=True)
    else:
        all_props.sort(key=lambda x: x.created_at, reverse=True)

    # ===== صفحه‌بندی =====
    paginator = Paginator(all_props, 12)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except Exception:
        page_obj = paginator.page(1)

    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'properties/property_list.html', {
        'properties': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'current_status': status,
        'current_type': property_type,
        'current_min_area': min_area,
        'current_max_area': max_area,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_bedrooms': bedrooms,
        'current_location_phase': location_phase,
        'current_sort': sort,
        'location_choices': ResidentialProperty.LOCATION_CHOICES,
        'query_string': query_params.urlencode(),
    })


def property_detail(request, pk, property_type):
    from django.contrib.contenttypes.models import ContentType
    from .models import PropertyImage

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

    # گرفتن عکس‌ها
    ct = ContentType.objects.get_for_model(prop)
    images = PropertyImage.objects.filter(
        content_type=ct,
        object_id=prop.id
    ).order_by('order')

    return render(request, 'properties/property_detail.html', {
        'prop': prop,
        'images': images,
    })


def construction_list(request):
    """لیست پروژه‌های ساخت و ساز"""
    project_type = request.GET.get('type', '')
    projects = ConstructionProject.objects.filter(is_active=True)
    if project_type:
        projects = projects.filter(project_type=project_type)
    return render(request, 'properties/construction_list.html', {
        'projects': projects,
        'current_type': project_type,
    })


@login_required
def property_create(request):
    if not request.user.can_post_property:
        messages.error(request, 'برای ثبت آگهی باید لایسنس فعال داشته باشید.')
        return redirect('properties:home')

    if request.method == 'POST':
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
        else:
            messages.error(request, 'نوع ملک نامعتبر است.')
            return redirect('properties:property_create')

        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.property_type = property_type
            prop.status = status
            prop.save()

            # آپلود عکس‌ها
            from .models import PropertyImage
            from django.contrib.contenttypes.models import ContentType
            images = request.FILES.getlist('images')
            if images:
                ct = ContentType.objects.get_for_model(prop)
                for idx, img in enumerate(images):
                    PropertyImage.objects.create(
                        content_type=ct,
                        object_id=prop.id,
                        image=img,
                        order=idx,
                    )

            messages.success(request, 'آگهی با موفقیت ثبت شد.')
            return redirect('properties:property_list')
        else:
            messages.error(request, f'خطا در فرم: {form.errors}')

    return render(request, 'properties/property_form.html', {
        'property_types': [
            ('villa', 'ویلایی'), ('apartment', 'آپارتمان'),
            ('commercial', 'تجاری'), ('office', 'اداری'),
            ('industrial', 'صنعتی'), ('land', 'زمین'), ('garden', 'باغ'),
        ],
        'status_choices': ResidentialProperty.STATUS_CHOICES,
    })

@login_required
def construction_create(request):
    """ثبت پروژه ساخت و ساز"""
    if not request.user.can_post_property:
        messages.error(request, 'برای ثبت پروژه باید لایسنس فعال داشته باشید.')
        return redirect('properties:home')

    if request.method == 'POST':
        form = ConstructionProjectForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            messages.success(request, 'پروژه با موفقیت ثبت شد.')
            return redirect('properties:construction_list')
        else:
            messages.error(request, f'خطا در فرم: {form.errors}')
    else:
        form = ConstructionProjectForm()

    return render(request, 'properties/construction_form.html', {'form': form})

# ============================================================
# ویرایش و حذف آگهی
# ============================================================

def _get_property_model(property_type):
    """برگرداندن مدل بر اساس نوع ملک"""
    model_map = {
        'residential': ResidentialProperty,
        'industrial': IndustrialProperty,
        'land': LandProperty,
        'garden': GardenProperty,
    }
    return model_map.get(property_type)


def _get_property_form(property_type):
    """برگرداندن فرم بر اساس نوع ملک"""
    form_map = {
        'residential': ResidentialPropertyForm,
        'industrial': IndustrialPropertyForm,
        'land': LandPropertyForm,
        'garden': GardenPropertyForm,
    }
    return form_map.get(property_type)


@login_required
def property_update(request, pk, property_type):
    """ویرایش آگهی - فقط صاحب آگهی یا مدیر"""
    Model = _get_property_model(property_type)
    FormClass = _get_property_form(property_type)
    if not Model or not FormClass:
        messages.error(request, 'نوع ملک نامعتبر است.')
        return redirect('properties:property_list')

    prop = get_object_or_404(Model, pk=pk)

    # چک دسترسی: صاحب آگهی یا admin/superadmin
    if prop.owner != request.user and request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('شما اجازه ویرایش این آگهی را ندارید.')

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=prop)
        if form.is_valid():
            form.save()

            # آپلود عکس‌های جدید (در صورت وجود)
            from .models import PropertyImage
            from django.contrib.contenttypes.models import ContentType
            images = request.FILES.getlist('images')
            if images:
                ct = ContentType.objects.get_for_model(prop)
                for idx, img in enumerate(images):
                    PropertyImage.objects.create(
                        content_type=ct,
                        object_id=prop.id,
                        image=img,
                        order=idx,
                    )

            messages.success(request, 'آگهی با موفقیت ویرایش شد.')
            return redirect('properties:property_detail', pk=prop.pk, property_type=property_type)
        else:
            messages.error(request, f'خطا در فرم: {form.errors}')
    else:
        form = FormClass(instance=prop)

    # عکس‌های موجود
    from .models import PropertyImage
    from django.contrib.contenttypes.models import ContentType
    ct = ContentType.objects.get_for_model(prop)
    existing_images = PropertyImage.objects.filter(content_type=ct, object_id=prop.id)

    return render(request, 'properties/property_form.html', {
        'form': form,
        'prop': prop,
        'existing_images': existing_images,
        'is_edit': True,
        'property_type': property_type,
        'property_types': [
            ('villa', 'ویلایی'), ('apartment', 'آپارتمان'),
            ('commercial', 'تجاری'), ('office', 'اداری'),
            ('industrial', 'صنعتی'), ('land', 'زمین'), ('garden', 'باغ'),
        ],
        'status_choices': ResidentialProperty.STATUS_CHOICES,
    })


@login_required
def property_delete(request, pk, property_type):
    """حذف آگهی - فقط صاحب آگهی یا مدیر"""
    Model = _get_property_model(property_type)
    if not Model:
        messages.error(request, 'نوع ملک نامعتبر است.')
        return redirect('properties:property_list')

    prop = get_object_or_404(Model, pk=pk)

    if prop.owner != request.user and request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('شما اجازه حذف این آگهی را ندارید.')

    if request.method == 'POST':
        # حذف عکس‌ها هم
        from .models import PropertyImage
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(prop)
        PropertyImage.objects.filter(content_type=ct, object_id=prop.id).delete()

        prop.delete()
        messages.success(request, 'آگهی با موفقیت حذف شد.')
        return redirect('accounts:dashboard')

    # صفحه تایید حذف
    return render(request, 'properties/property_confirm_delete.html', {'prop': prop, 'property_type': property_type})


@login_required
def property_image_delete(request, image_id):
    """حذف یک عکس از آگهی"""
    from .models import PropertyImage
    img = get_object_or_404(PropertyImage, id=image_id)
    prop = img.content_object

    # چک دسترسی
    if prop.owner != request.user and request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    # تشخیص property_type
    type_map = {
        'ResidentialProperty': 'residential',
        'IndustrialProperty': 'industrial',
        'LandProperty': 'land',
        'GardenProperty': 'garden',
    }
    ptype = type_map.get(prop.__class__.__name__, 'residential')

    img.delete()
    messages.success(request, 'عکس حذف شد.')
    return redirect('properties:property_update', pk=prop.pk, property_type=ptype)

