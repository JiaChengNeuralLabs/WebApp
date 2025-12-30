# -*- coding: utf-8 -*-
from django import forms
from .models import Student, Voucher, Payment, LicenseType, Vehicle, Maintenance, Practice, TaxInvoice


class StudentForm(forms.ModelForm):
    """Formulario para crear/editar alumnos"""

    class Meta:
        model = Student
        fields = [
            'expedition_number', 'first_name', 'last_name', 'dni', 'email', 'phone',
            'address', 'street_address', 'postal_code', 'municipality', 'province',
            'license_type', 'is_active', 'notes'
        ]
        widgets = {
            'expedition_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de expediente (opcional)'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (opcional)'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefono'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Direccion completa (opcional)'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle y numero'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Codigo postal', 'style': 'width: 120px;'}),
            'municipality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Municipio'}),
            'province': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Provincia'}),
            'license_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        }


class VoucherForm(forms.ModelForm):
    """Formulario para anadir cargos/conceptos"""

    # Campo adicional para fecha de práctica (solo visible cuando es práctica)
    practice_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_practice_date'
        }),
        label='Fecha de la práctica'
    )

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

    def clean(self):
        cleaned_data = super().clean()
        concept_type = cleaned_data.get('concept_type')
        practice_date = cleaned_data.get('practice_date')

        # Si es una práctica individual, la fecha es obligatoria
        practice_types = ['PRACTICE_90', 'PRACTICE_60', 'PRACTICE_45', 'PRACTICE_30']
        if concept_type in practice_types and not practice_date:
            self.add_error('practice_date', 'La fecha es obligatoria para las prácticas')

        return cleaned_data


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


class TaxInvoiceForm(forms.ModelForm):
    """Formulario para crear facturas trimestrales con tasas DGT"""

    # Seleccion de pagos a incluir
    selected_payments = forms.ModelMultipleChoiceField(
        queryset=Payment.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Pagos a incluir"
    )

    # Total pagado (puede ingresarse manualmente o calcularse desde pagos)
    total_paid = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'id': 'id_total_paid',
            'placeholder': 'Total pagado en euros'
        }),
        label="Total pagado"
    )

    class Meta:
        model = TaxInvoice
        fields = [
            'fecha', 'curso',
            'has_tasa_basica', 'has_tasa_a', 'has_traslado', 'renovaciones_count',
            'notes'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'curso': forms.Select(attrs={'class': 'form-control'}),
            'has_tasa_basica': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_tasa_a': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_traslado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'renovaciones_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'style': 'width: 80px;'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        if student:
            # Filtrar pagos de este alumno que no tienen factura trimestral
            self.fields['selected_payments'].queryset = Payment.objects.filter(
                student=student
            ).exclude(
                tax_invoices__isnull=False
            ).order_by('-date_paid')

            # Pre-rellenar curso basado en el tipo de carnet del alumno
            curso_map = {
                'B': 'B', 'A': 'A', 'A1': 'A1', 'A2': 'A2', 'AM': 'AM',
                'C': 'C', 'D': 'B', 'BE': 'B'
            }
            license_name = student.license_type.name if student.license_type else 'B'
            self.initial['curso'] = curso_map.get(license_name, 'B')
