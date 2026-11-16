from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # پنل مدیریت سایت
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/licenses/', views.admin_licenses, name='admin_licenses'),
    path('admin-panel/licenses/<int:license_id>/<str:action>/', views.admin_license_action, name='admin_license_action'),
    path('admin-panel/agencies/', views.admin_agencies, name='admin_agencies'),
    path('admin-panel/agencies/<int:user_id>/create-license/', views.admin_create_license, name='admin_create_license'),
    # مدیریت آگهی‌ها
    path('admin-panel/properties/', views.admin_properties, name='admin_properties'),
    path('admin-panel/properties/<str:property_type>/<int:pk>/<str:action>/', views.admin_property_action, name='admin_property_action'),
    path('admin-panel/licenses/<int:license_id>/renew/', views.admin_license_renew, name='admin_license_renew'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]