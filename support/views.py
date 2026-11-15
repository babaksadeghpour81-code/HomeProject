from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import LoanRequestForm


def loan_request(request):
    """فرم درخواست وام بانکی"""
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            if request.user.is_authenticated:
                obj.user = request.user
            obj.save()
            messages.success(request, 'درخواست وام شما ثبت شد. کارشناسان ما با شما تماس خواهند گرفت.')
            return redirect('support:loan_request')
    else:
        form = LoanRequestForm()

    return render(request, 'support/loan_request.html', {'form': form})

def contact(request):
    """صفحه پشتیبان و ارتباط با ما"""
    return render(request, 'support/contact.html')


def about(request):
    """درباره دپارتمان املاک اندیشه"""
    return render(request, 'support/about.html')