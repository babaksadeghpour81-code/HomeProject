from django.urls import path
from . import views

app_name = 'agencies'

urlpatterns = [
    path('', views.agency_list, name='agency_list'),
]