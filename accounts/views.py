from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import random
from .forms import RegisterForm
from .models import User, License, PasswordResetOTP


def register(request):
    if request.user.is_authenticated:
        return redirect('properties:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
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

    license_obj = getattr(request.user, 'license_info', None)
    license_warning = None
    if license_obj and license_obj.is_valid:
        days_left = (license_obj.expires_at - timezone.now()).days
        if days_left <= 30:
            license_warning = f'⚠️ لایسنس شما تا {days_left} روز دیگر منقضی می‌شود. لطفاً تمدید کنید.'
    elif license_obj and not license_obj.is_valid:
        license_warning = '⚠️ لایسنس شما منقضی شده. برای ثبت آگهی با مدیریت تماس بگیرید.'

    context = {
        'license': license_obj,
        'license_warning': license_warning,
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
        ResidentialProperty, IndustrialProperty, LandProperty, GardenProperty, ConstructionProject
    )
    from support.models import LoanRequest

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
        'total_constructions': ConstructionProject.objects.count(),
        'pending_loans': LoanRequest.objects.filter(status='pending').count(),
    }

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

@login_required
def admin_license_renew(request, license_id):
    """تمدید لایسنس توسط مدیر"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    license_obj = get_object_or_404(License, id=license_id)

    if request.method == 'POST':
        from datetime import timedelta
        duration_days = int(request.POST.get('duration_days', 365))
        amount = int(request.POST.get('amount', 0))

        # اگر لایسنس منقضی شده، از الان تمدید کن
        if license_obj.expires_at < timezone.now():
            license_obj.expires_at = timezone.now() + timedelta(days=duration_days)
        else:
            license_obj.expires_at += timedelta(days=duration_days)

        license_obj.is_active = True
        license_obj.status = 'active'
        license_obj.amount_paid += amount
        license_obj.save()

        messages.success(request, f'لایسنس {license_obj.agency.agency_name} به مدت {duration_days} روز تمدید شد.')
        return redirect('accounts:admin_licenses')

    return render(request, 'accounts/admin_license_renew.html', {'license': license_obj})

@login_required
def profile_edit(request):
    """ویرایش پروفایل آژانس"""
    if request.user.role not in ('agency', 'admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    from .forms import AgencyProfileForm

    if request.method == 'POST':
        form = AgencyProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل با موفقیت به‌روزرسانی شد.')
            return redirect('accounts:profile_edit')
    else:
        form = AgencyProfileForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})

# ============================================================
# مدیریت پروژه‌های ساخت و ساز (پنل مدیر سایت)
# ============================================================

@login_required
def admin_constructions(request):
    """مدیریت پروژه‌های ساخت و ساز"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    from properties.models import ConstructionProject
    from django.core.paginator import Paginator

    projects = ConstructionProject.objects.all().order_by('-created_at')

    # فیلتر بر اساس وضعیت
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        projects = projects.filter(is_active=True)
    elif status_filter == 'inactive':
        projects = projects.filter(is_active=False)

    # فیلتر بر اساس نوع پروژه
    type_filter = request.GET.get('type', '')
    if type_filter in ('presale', 'partnership'):
        projects = projects.filter(project_type=type_filter)

    # صفحه‌بندی
    paginator = Paginator(projects, 15)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except Exception:
        page_obj = paginator.page(1)

    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'accounts/admin_constructions.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'current_status': status_filter,
        'current_type': type_filter,
        'query_string': query_params.urlencode(),
    })


@login_required
def admin_construction_action(request, pk, action):
    """فعال/غیرفعال/حذف پروژه ساخت و ساز"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    from properties.models import ConstructionProject

    project = get_object_or_404(ConstructionProject, pk=pk)

    if action == 'activate':
        project.is_active = True
        project.save()
        messages.success(request, f'پروژه «{project.title}» فعال شد.')
    elif action == 'deactivate':
        project.is_active = False
        project.save()
        messages.warning(request, f'پروژه «{project.title}» غیرفعال شد.')
    elif action == 'delete':
        project.delete()
        messages.info(request, 'پروژه حذف شد.')

    return redirect('accounts:admin_constructions')


# ============================================================
# مدیریت درخواست‌های وام بانکی (پنل مدیر سایت)
# ============================================================

@login_required
def admin_loans(request):
    """مدیریت درخواست‌های وام"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    from support.models import LoanRequest
    from django.core.paginator import Paginator

    loans = LoanRequest.objects.all().order_by('-created_at')

    # فیلتر بر اساس وضعیت
    status_filter = request.GET.get('status', '')
    if status_filter:
        loans = loans.filter(status=status_filter)

    # فیلتر بر اساس نوع وام
    type_filter = request.GET.get('type', '')
    if type_filter:
        loans = loans.filter(loan_type=type_filter)

    # صفحه‌بندی
    paginator = Paginator(loans, 15)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except Exception:
        page_obj = paginator.page(1)

    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'accounts/admin_loans.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'current_status': status_filter,
        'current_type': type_filter,
        'status_choices': LoanRequest.STATUS_CHOICES,
        'loan_type_choices': LoanRequest.LOAN_TYPE_CHOICES,
        'query_string': query_params.urlencode(),
    })


@login_required
def admin_loan_detail(request, loan_id):
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    from support.models import LoanRequest

    loan = get_object_or_404(LoanRequest, id=loan_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_note = request.POST.get('admin_note', '').strip()

        if new_status in dict(LoanRequest.STATUS_CHOICES):
            loan.status = new_status
            loan.admin_note = admin_note
            loan.save()
            messages.success(request, 'وضعیت درخواست وام به‌روزرسانی شد.')
            return redirect('accounts:admin_loans')

    return render(request, 'accounts/admin_loan_detail.html', {
        'loan': loan,
        'status_choices': LoanRequest.STATUS_CHOICES,
    })


@login_required
def admin_loan_delete(request, loan_id):
    """حذف درخواست وام"""
    if request.user.role not in ('admin', 'superadmin'):
        return HttpResponseForbidden('دسترسی غیرمجاز')

    from support.models import LoanRequest

    loan = get_object_or_404(LoanRequest, id=loan_id)
    loan.delete()
    messages.info(request, 'درخواست وام حذف شد.')
    return redirect('accounts:admin_loans')

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def _send_otp_sms(phone, otp_code):
    """ارسال کد OTP با sms_ir"""
    try:
        from sms_ir import SmsIr

        sms_ir = SmsIr(
            settings.SMS_IR_API_KEY,
            settings.SMS_IR_LINE_NUMBER,
        )
        sms_ir.send_verify_code(
            phone,
            settings.SMS_IR_TEMPLATE_ID,
            [{'name': 'CODE', 'value': otp_code}]
        )
        return True, 'کد تایید ارسال شد.'
    except Exception as e:
        import traceback
        print(f"SMS Error: {e}")
        print(traceback.format_exc())
        return False, f'خطا در ارسال پیامک: {e}'


@login_required
def password_change(request):
    """تغییر رمز عبور توسط کاربر لاگین‌شده (با رمز فعلی)"""
    from .forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()

            # به‌روزرسانی session تا کاربر لاگین بماند
            update_session_auth_hash(request, user)

            messages.success(request, 'رمز عبور شما با موفقیت تغییر کرد. سایر دستگاه‌ها از حساب خارج شدند.')
            return redirect('accounts:password_change')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})


def password_reset_request(request):
    """مرحله ۱: دریافت کد ملی و ارسال OTP"""
    from .forms import PasswordResetRequestForm

    if request.user.is_authenticated:
        return redirect('properties:home')

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            national_code = form.cleaned_data['national_code']

            user = User.objects.filter(username=national_code, is_active=True).first()

            if not user:
                messages.error(request, 'کاربری با این کد ملی یافت نشد.')
                return render(request, 'accounts/password_reset_request.html', {'form': form})

            phone = user.phone_number or user.agency_phone
            if not phone:
                messages.error(request, 'شماره موبایلی برای این حساب ثبت نشده است. با مدیریت تماس بگیرید.')
                return render(request, 'accounts/password_reset_request.html', {'form': form})

            # بررسی محدودیت
            last_24h = timezone.now() - timedelta(hours=24)
            request_count = user.password_reset_otps.filter(
                created_at__gte=last_24h
            ).count()

            if request_count >= settings.OTP_MAX_REQUESTS_PER_DAY:
                messages.error(
                    request,
                    f'شما در ۲۴ ساعت گذشته {settings.OTP_MAX_REQUESTS_PER_DAY} بار درخواست داده‌اید. '
                    f'لطفاً بعداً تلاش کنید یا با مدیریت تماس بگیرید.'
                )
                return render(request, 'accounts/password_reset_request.html', {'form': form})

            # تولید و ذخیره OTP
            otp_code = str(random.randint(100000, 999999))
            PasswordResetOTP.objects.create(
                user=user,
                otp_code=otp_code,
                phone=phone,
                expires_at=timezone.now() + timedelta(seconds=settings.OTP_EXPIRY_SECONDS),
                ip_address=_get_client_ip(request),
            )

            # ارسال پیامک
            success, msg = _send_otp_sms(phone, otp_code)

            if success:
                request.session['reset_user_id'] = user.id
                request.session['reset_phone'] = phone
                messages.success(request, f'کد تایید به شماره {phone} ارسال شد.')
                return redirect('accounts:password_reset_verify')
            else:
                messages.error(request, msg)
                return render(request, 'accounts/password_reset_request.html', {'form': form})
    else:
        form = PasswordResetRequestForm()

    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_verify(request):
    """مرحله ۲: تایید OTP و تغییر رمز"""
    from .forms import PasswordResetVerifyForm

    user_id = request.session.get('reset_user_id')
    phone = request.session.get('reset_phone')

    if not user_id:
        messages.error(request, 'لطفاً ابتدا کد ملی خود را وارد کنید.')
        return redirect('accounts:password_reset')

    otp_obj = PasswordResetOTP.objects.filter(
        user_id=user_id,
        is_used=False,
        expires_at__gt=timezone.now(),
    ).order_by('-created_at').first()

    if not otp_obj:
        messages.error(request, 'کد تایید منقضی شده است. لطفاً دوباره درخواست دهید.')
        return redirect('accounts:password_reset')

    if request.method == 'POST':
        form = PasswordResetVerifyForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['otp_code']
            new_password = form.cleaned_data['new_password1']

            if entered_code != otp_obj.otp_code:
                form.add_error('otp_code', 'کد تایید اشتباه است.')
            else:
                user = otp_obj.user
                user.set_password(new_password)
                user.save()

                otp_obj.is_used = True
                otp_obj.save()

                request.session.pop('reset_user_id', None)
                request.session.pop('reset_phone', None)

                messages.success(request, 'رمز عبور با موفقیت تغییر کرد. اکنون می‌توانید وارد شوید.')
                return redirect('accounts:login')
    else:
        form = PasswordResetVerifyForm()

    return render(request, 'accounts/password_reset_verify.html', {
        'form': form,
        'phone': phone,
    })