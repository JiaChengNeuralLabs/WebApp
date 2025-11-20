# -*- coding: utf-8 -*-
from django import forms
from .models import Student, Voucher, Payment, LicenseType


class StudentForm(forms.ModelForm):
    """Formulario para crear/editar alumnos"""

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'dni', 'email', 'phone', 'address', 'license_type', 'is_active', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (opcional)'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefono'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Direccion (opcional)'}),
            'license_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        }


class VoucherForm(forms.ModelForm):
    """Formulario para anadir cargos/conceptos"""

    class Meta:
        model = Voucher
        fields = ['concept_type', 'amount', 'description']
        widgets = {
            'concept_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_concept_type'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'id': 'id_amount',
                'placeholder': 'Importe en euros'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripcion adicional (opcional)',
                'id': 'id_description'
            }),
        }
        labels = {
            'concept_type': 'Concepto',
            'amount': 'Importe (€)',
            'description': 'Descripción adicional'
        }


class PaymentForm(forms.ModelForm):
    """Formulario para registrar pagos"""

    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Cantidad pagada'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas adicionales (opcional)'}),
        }
