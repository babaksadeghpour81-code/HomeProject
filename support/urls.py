from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # فرم ثبت درخواست وام
    path('loan/', views.loan_request, name='loan_request'),

    # پیگیری درخواست (فرم ورود کد)
    path('loan/tracking/', views.loan_tracking, name='loan_tracking'),

    # پیگیری با کد مشخص
    path('loan/tracking/<str:tracking_code>/', views.loan_tracking, name='loan_tracking_detail'),

    # لیست درخواست‌های من
    path('loan/my/', views.my_loan_requests, name='my_loan_requests'),

    # صفحات پشتیبان
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]