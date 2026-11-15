from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.home, name='home'),
    path('properties/', views.property_list, name='property_list'),
    path('properties/create/', views.property_create, name='property_create'),

    # ویرایش و حذف باید قبل از detail باشند
    path('properties/image/<int:image_id>/delete/', views.property_image_delete, name='property_image_delete'),
    path('properties/<int:pk>/<str:property_type>/edit/', views.property_update, name='property_update'),
    path('properties/<int:pk>/<str:property_type>/delete/', views.property_delete, name='property_delete'),

    # detail آخر
    path('properties/<int:pk>/<str:property_type>/', views.property_detail, name='property_detail'),

    # construction
    path('construction/', views.construction_list, name='construction_list'),
    path('construction/create/', views.construction_create, name='construction_create'),
]