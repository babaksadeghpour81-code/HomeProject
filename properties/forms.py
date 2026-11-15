from django import forms
from .models import (
    ResidentialProperty, IndustrialProperty,
    LandProperty, GardenProperty
)
from .models import ConstructionProject

class BasePropertyForm(forms.ModelForm):
    """فرم پایه برای فیلدهای مشترک"""

    class Meta:
        fields = ['title', 'description', 'price', 'deposit', 'rent', 'video_url', 'video_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان آگهی'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'قیمت کل (تومان)'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ودیعه (تومان)'}),
            'rent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'اجاره ماهیانه (تومان)'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'لینک ویدیو'}),
        }


class ResidentialPropertyForm(BasePropertyForm):
    class Meta(BasePropertyForm.Meta):
        model = ResidentialProperty
        fields = BasePropertyForm.Meta.fields + [
            'location_phase', 'location_text', 'area', 'bedrooms',
            'floor', 'total_floors', 'units_per_floor', 'building_age',
            'has_elevator', 'has_storage', 'has_parking', 'has_balcony', 'amenities',
        ]
        widgets = {
            **BasePropertyForm.Meta.widgets,
            'location_phase': forms.Select(attrs={'class': 'form-control'}),
            'location_text': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'متراژ'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'units_per_floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'building_age': forms.NumberInput(attrs={'class': 'form-control'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class IndustrialPropertyForm(BasePropertyForm):
    class Meta(BasePropertyForm.Meta):
        model = IndustrialProperty
        fields = BasePropertyForm.Meta.fields + ['usage', 'area']
        widgets = {
            **BasePropertyForm.Meta.widgets,
            'usage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کاربری'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'متراژ'}),
        }


class LandPropertyForm(BasePropertyForm):
    class Meta(BasePropertyForm.Meta):
        model = LandProperty
        fields = BasePropertyForm.Meta.fields + ['usage', 'area']
        widgets = {
            **BasePropertyForm.Meta.widgets,
            'usage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کاربری'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'متراژ'}),
        }


class GardenPropertyForm(BasePropertyForm):
    class Meta(BasePropertyForm.Meta):
        model = GardenProperty
        fields = BasePropertyForm.Meta.fields + ['area']
        widgets = {
            **BasePropertyForm.Meta.widgets,
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'متراژ'}),
        }

class ConstructionProjectForm(forms.ModelForm):
    class Meta:
        model = ConstructionProject
        fields = [
            'project_type', 'title', 'description', 'location_phase', 'location_text',
            'area', 'total_units', 'floors', 'price', 'start_date', 'delivery_date',
            'amenities', 'video_url'
        ]
        widgets = {
            'project_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location_phase': forms.Select(attrs={'class': 'form-control'}),
            'location_text': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_units': forms.NumberInput(attrs={'class': 'form-control'}),
            'floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

