from django.shortcuts import render
from accounts.models import User


def agency_list(request):
    """لیست عمومی آژانس‌های عضو"""
    agencies = User.objects.filter(
        role='agency',
        is_active=True
    ).order_by('agency_name')

    return render(request, 'agencies/agency_list.html', {'agencies': agencies})