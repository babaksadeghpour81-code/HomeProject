from django import forms
from .models import LoanRequest


class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ['full_name', 'national_code', 'phone', 'loan_type', 'amount', 'description']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'loan_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }