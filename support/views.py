from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .forms import LoanRequestForm
from .models import LoanRequest


@login_required
def loan_request(request):
    """فرم درخواست وام - فقط کاربران لاگین‌شده"""
    existing = LoanRequest.objects.filter(
        user=request.user,
        status__in=('pending', 'reviewing')
    ).first()

    if existing:
        messages.warning(
            request,
            f'شما یک درخواست در حال بررسی دارید (کد پیگیری: {existing.tracking_code}). '
            f'ابتدا وضعیت آن را پیگیری کنید.'
        )
        return redirect('support:loan_tracking_detail', tracking_code=existing.tracking_code)  # ← اصلاح

    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(
                request,
                f'درخواست شما با کد پیگیری «{obj.tracking_code}» ثبت شد. '
                f'این کد را برای پیگیری نگه دارید.'
            )
            return redirect('support:loan_tracking_detail', tracking_code=obj.tracking_code)  # ← اصلاح
    else:
        form = LoanRequestForm()

    return render(request, 'support/loan_request.html', {
        'form': form,
        'my_requests_count': LoanRequest.objects.filter(user=request.user).count(),
    })


def loan_tracking(request, tracking_code=None):
    """پیگیری درخواست وام"""
    if tracking_code is None:
        # اگر کد نداد، فرم ورود کد را نشان بده
        if request.method == 'POST':
            code = request.POST.get('tracking_code', '').strip().upper()
            if code:
                return redirect('support:loan_tracking_detail', tracking_code=code)  # ← اصلاح
            messages.error(request, 'لطفاً کد پیگیری را وارد کنید.')

        return render(request, 'support/loan_tracking_form.html')

    # اگر کد داد، درخواست را پیدا کن
    loan = LoanRequest.objects.filter(tracking_code=tracking_code.upper()).first()

    if not loan:
        messages.error(request, 'درخواستی با این کد پیگیری یافت نشد.')
        return redirect('support:loan_tracking')

    # اگر کاربر لاگین است و صاحب درخواست نیست، اجازه نده
    if loan.user and request.user.is_authenticated and loan.user != request.user:
        if request.user.role not in ('admin', 'superadmin'):
            messages.error(request, 'شما به این درخواست دسترسی ندارید.')
            return redirect('support:loan_tracking')

    return render(request, 'support/loan_tracking.html', {'loan': loan})


@login_required
def my_loan_requests(request):
    """لیست درخواست‌های وام کاربر"""
    loans = LoanRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'support/my_loan_requests.html', {'loans': loans})

def contact(request):
    """صفحه پشتیبان و ارتباط با ما"""
    return render(request, 'support/contact.html')


def about(request):
    """درباره دپارتمان املاک اندیشه"""
    return render(request, 'support/about.html')

