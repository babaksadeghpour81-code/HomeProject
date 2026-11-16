from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone

from .forms import RegisterForm
from .models import User, License


def register(request):
    if request.user.is_authenticated:
        return redirect('properties:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'ثبت‌نام با موفقیت انجام شد. برای ثبت آگهی نیاز به لایسنس فعال دارید.'
            )
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    """داشبورد آژانس"""
    if request.user.role == 'user':
        messages.info(request, 'برای دسترسی به داشبورد آژانس، باید آژانس باشید.')
        return redirect('properties:home')

    # گرفتن لایسنس کاربر (اگر دارد)
    license_obj = getattr(request.user, 'license_info', None)

    # گرفتن آگهی‌های کاربر از همه مدل‌ها
    from properties.models import (
        ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty
    )
    my_properties = []
    for Model in [ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty]:
        my_properties += list(Model.objects.filter(owner=request.user))

    my_properties.sort(key=lambda x: x.created_at, reverse=True)

    # آمار
    stats = {
        'total': len(my_properties),
        'active': sum(1 for p in my_properties if p.is_active),
        'inactive': sum(1 for p in my_properties if not p.is_active),
    }

    context = {
        'license': license_obj,
        'properties': my_properties,
        'stats': stats,
        'now': timezone.now(),
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def admin_panel(request):
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    from properties.models import (
        ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty
    )
    all_props = []
    for Model in [ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty]:
        all_props += list(Model.objects.all())

    stats = {
        'total_properties': len(all_props),
        'active_properties': sum(1 for p in all_props if p.is_active),
        'inactive_properties': sum(1 for p in all_props if not p.is_active),
        'total_agencies': User.objects.filter(role='agency').count(),
        'pending_licenses': License.objects.filter(status='pending').count(),
        'active_licenses': License.objects.filter(status='active', is_active=True).count(),
    }

    # آخرین آگهی‌ها
    recent = sorted(all_props, key=lambda x: x.created_at, reverse=True)[:10]

    return render(request, 'accounts/admin_panel.html', {
        'stats': stats,
        'recent_properties': recent,
    })


@login_required
def admin_licenses(request):
    """مدیریت لایسنس‌ها"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    licenses = License.objects.select_related('agency').all().order_by('-issued_at')

    return render(request, 'accounts/admin_licenses.html', {'licenses': licenses})


@login_required
def admin_license_action(request, license_id, action):
    """تایید/رد/تمدید لایسنس"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    license_obj = get_object_or_404(License, id=license_id)

    if action == 'approve':
        license_obj.status = 'active'
        license_obj.is_active = True
        license_obj.save()
        # فعال کردن پرچم روی کاربر
        license_obj.agency.is_license_active = True
        license_obj.agency.save()
        messages.success(request, f'لایسنس {license_obj.agency.agency_name} تایید شد.')
    elif action == 'reject':
        license_obj.status = 'rejected'
        license_obj.is_active = False
        license_obj.save()
        license_obj.agency.is_license_active = False
        license_obj.agency.save()
        messages.warning(request, f'لایسنس {license_obj.agency.agency_name} رد شد.')
    elif action == 'delete':
        license_obj.delete()
        messages.info(request, 'لایسنس حذف شد.')

    return redirect('accounts:admin_licenses')


@login_required
def admin_agencies(request):
    """مدیریت آژانس‌ها"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    agencies = User.objects.filter(role='agency').order_by('-date_joined')

    return render(request, 'accounts/admin_agencies.html', {'agencies': agencies})


@login_required
def admin_create_license(request, user_id):
    """صدور لایسنس برای یک آژانس (فقط مدیر)"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    agency = get_object_or_404(User, id=user_id, role='agency')

    # اگر از قبل لایسنس دارد و فعال است، خطا
    if hasattr(agency, 'license_info'):
        messages.warning(request, 'این آژانس قبلاً لایسنس دارد. ابتدا آن را حذف یا غیرفعال کنید.')
        return redirect('accounts:admin_agencies')

    if request.method == 'POST':
        import uuid
        from datetime import timedelta

        duration_days = int(request.POST.get('duration_days', 365))
        amount = int(request.POST.get('amount', 0))

        License.objects.create(
            agency=agency,
            license_key=uuid.uuid4().hex[:20].upper(),
            expires_at=timezone.now() + timedelta(days=duration_days),
            is_active=True,
            status='active',
            amount_paid=amount,
        )
        agency.is_license_active = True
        agency.save()

        messages.success(request, f'لایسنس برای {agency.agency_name} صادر شد.')
        return redirect('accounts:admin_agencies')

    return render(request, 'accounts/admin_create_license.html', {'agency': agency})

@login_required
def admin_properties(request):
    """مدیریت همه آگهی‌ها"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    from properties.models import (
        ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty
    )
    from django.core.paginator import Paginator

    all_props = []
    for Model in [ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty]:
        all_props += list(Model.objects.all())

    # مرتب‌سازی: جدیدترین اول
    all_props.sort(key=lambda x: x.created_at, reverse=True)

    # فیلتر بر اساس وضعیت
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        all_props = [p for p in all_props if p.is_active]
    elif status_filter == 'inactive':
        all_props = [p for p in all_props if not p.is_active]

    # صفحه‌بندی
    paginator = Paginator(all_props, 15)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except Exception:
        page_obj = paginator.page(1)

    return render(request, 'accounts/admin_properties.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'current_status': status_filter,
        'query_string': request.GET.urlencode() if request.GET else '',
    })


@login_required
def admin_property_action(request, property_type, pk, action):
    """تایید/رد/حذف آگهی توسط مدیر"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    from properties.models import (
        ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty, PropertyImage
    )
    from django.contrib.contenttypes.models import ContentType

    model_map = {
        'residential': ResidentialProperty,
        'industrial': IndustrialProperty,
        'land': LandProperty,
        'garden': GardenProperty,
    }
    Model = model_map.get(property_type)
    if not Model:
        messages.error(request, 'نوع ملک نامعتبر است.')
        return redirect('accounts:admin_properties')

    prop = get_object_or_404(Model, pk=pk)

    if action == 'activate':
        prop.is_active = True
        prop.save()
        messages.success(request, f'آگهی «{prop.title}» فعال شد.')
    elif action == 'deactivate':
        prop.is_active = False
        prop.save()
        messages.warning(request, f'آگهی «{prop.title}» غیرفعال شد.')
    elif action == 'delete':
        # حذف عکس‌ها
        ct = ContentType.objects.get_for_model(prop)
        PropertyImage.objects.filter(content_type=ct, object_id=prop.id).delete()
        prop.delete()
        messages.info(request, f'آگهی حذف شد.')

    return redirect('accounts:admin_properties')

