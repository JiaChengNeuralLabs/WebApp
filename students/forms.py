# -*- coding: utf-8 -*-
from django import forms
from .models import Student, Voucher, Payment, LicenseType, Vehicle, Maintenance, Practice


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


class VehicleForm(forms.ModelForm):
    """Formulario para crear/editar vehiculos"""

    class Meta:
        model = Vehicle
        fields = ['license_plate', 'brand', 'model', 'year', 'vehicle_type', 'color', 'is_active', 'notes']
        widgets = {
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1234 ABC'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Renault'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Clio'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2024'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Blanco'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        }


class MaintenanceForm(forms.ModelForm):
    """Formulario para registrar mantenimientos"""

    class Meta:
        model = Maintenance
        fields = ['maintenance_type', 'description', 'brand', 'model', 'cost', 'mileage', 'maintenance_date', 'next_maintenance_date']
        widgets = {
            'maintenance_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripcion del mantenimiento'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marca del repuesto (opcional)'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Modelo del repuesto (opcional)'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Coste en euros'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Kilometraje actual'}),
            'maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PracticeForm(forms.ModelForm):
    """Formulario para registrar practicas"""

    class Meta:
        model = Practice
        fields = ['duration', 'practice_date', 'notes']
        widgets = {
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'practice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notas (opcional)'}),
        }
