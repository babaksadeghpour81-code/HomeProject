from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from accounts.models import User
from properties.models import (
    ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty
)


def agency_list(request):
    """لیست عمومی آژانس‌های عضو"""
    agencies = User.objects.filter(
        role='agency',
        is_active=True
    ).order_by('agency_name')

    return render(request, 'agencies/agency_list.html', {'agencies': agencies})


def agency_detail(request, agency_id):
    """پروفایل عمومی یک آژانس + آگهی‌هایش"""
    agency = get_object_or_404(User, id=agency_id, role='agency', is_active=True)

    # گرفتن همه آگهی‌های فعال این آژانس
    all_props = []
    for Model in [ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty]:
        all_props += list(Model.objects.filter(owner=agency, is_active=True))

    all_props.sort(key=lambda x: x.created_at, reverse=True)

    # صفحه‌بندی
    paginator = Paginator(all_props, 9)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except Exception:
        page_obj = paginator.page(1)

    # بررسی لایسنس
    license_obj = getattr(agency, 'license_info', None)

    return render(request, 'agencies/agency_detail.html', {
        'agency': agency,
        'page_obj': page_obj,
        'paginator': paginator,
        'license': license_obj,
    })