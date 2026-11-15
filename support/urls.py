from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('loan/', views.loan_request, name='loan_request'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]