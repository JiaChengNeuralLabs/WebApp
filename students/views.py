"""
Vistas para Autoescuela Carrasco - Sistema de Gestión de Alumnos

Este archivo contiene 10 vistas principales:
0. landing_page - Página principal pública (sin @login_required)
1. user_login - Login (sin @login_required)
2. user_logout - Logout
3. student_list - Lista de alumnos con búsqueda por nombre/DNI/teléfono
4. student_create - Crear nuevo alumno
5. student_detail - Detalle del alumno con resumen financiero completo
6. student_edit - Editar alumno existente
7. student_delete - Eliminar alumno (con confirmación)
8. voucher_create - Añadir bono de prácticas al alumno
9. payment_create - Registrar pago del alumno
10. upload_receipt - Subir recibo (pública, sin login)

Todas las vistas excepto landing_page, login, logout y upload_receipt requieren autenticación (@login_required).
Los pagos se registran con el usuario que los creó (created_by).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Student, LicenseType, Voucher, Payment, AuditLog, Vehicle, Maintenance, Practice, Invoice, TaxInvoice
from .forms import StudentForm, VoucherForm, PaymentForm, VehicleForm, MaintenanceForm, PracticeForm, TaxInvoiceForm


def landing_page(request):
    """Vista de la página principal / landing page"""
    # Si el usuario ya está autenticado, redirigir al panel
    if request.user.is_authenticated:
        return redirect('student_list')

    return render(request, 'students/landing_page.html')


def user_login(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('student_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Registrar inicio de sesión en el log
            AuditLog.log_action(
                user=user,
                action='LOGIN',
                entity_type='USER',
                entity_id=user.id,
                entity_name=user.username,
                description=f'Usuario {user.username} inició sesión',
                request=request
            )
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('student_list')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'students/login.html')


def user_logout(request):
    """Vista de cierre de sesión"""
    # Registrar cierre de sesión antes de hacer logout
    if request.user.is_authenticated:
        AuditLog.log_action(
            user=request.user,
            action='LOGOUT',
            entity_type='USER',
            entity_id=request.user.id,
            entity_name=request.user.username,
            description=f'Usuario {request.user.username} cerró sesión',
            request=request
        )
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('login')


@login_required
def student_list(request):
    """Lista de alumnos con búsqueda"""
    query = request.GET.get('q', '')
    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(dni__icontains=query) |
            Q(phone__icontains=query)
        )

    context = {
        'students': students,
        'query': query,
    }
    return render(request, 'students/student_list.html', context)


@login_required
def student_create(request):
    """Crear nuevo alumno"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.created_by = request.user
            student.save()
            # Registrar creación de alumno en el log
            AuditLog.log_action(
                user=request.user,
                action='CREATE',
                entity_type='STUDENT',
                entity_id=student.id,
                entity_name=str(student),
                description=f'Alumno creado: {student.first_name} {student.last_name} (DNI: {student.dni})',
                request=request
            )
            messages.success(request, f'Alumno {student} creado correctamente')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm()

    return render(request, 'students/student_form.html', {'form': form, 'title': 'Nuevo Alumno'})


@login_required
def student_detail(request, pk):
    """Detalle del alumno con información financiera"""
    from django.db.models import Sum

    student = get_object_or_404(Student, pk=pk)
    vouchers = student.vouchers.all()
    payments = student.payments.all()
    practices = student.practices.all().order_by('-practice_date')

    # Calcular minutos de prácticas (todas las facturadas individualmente)
    practices_for_bonus = Practice.objects.filter(
        student=student,
        is_billed=True,
        billed_voucher__concept_type__in=['PRACTICE_90', 'PRACTICE_60', 'PRACTICE_45', 'PRACTICE_30']
    )
    total_practice_minutes = practices_for_bonus.aggregate(total=Sum('duration'))['total'] or 0

    # Calcular minutos restantes para el próximo descuento
    minutes_for_bonus = 450 - (total_practice_minutes % 450) if total_practice_minutes > 0 else 450

    context = {
        'student': student,
        'vouchers': vouchers,
        'payments': payments,
        'practices': practices,
        'unbilled_minutes': total_practice_minutes % 450,  # Minutos hacia el próximo bono
        'total_practice_minutes': total_practice_minutes,
        'minutes_for_bonus': minutes_for_bonus,
        'total_debt': student.get_total_debt(),
        'total_paid': student.get_total_paid(),
        'balance': student.get_balance(),
        'pending_amount': student.get_pending_amount(),
    }
    return render(request, 'students/student_detail.html', context)


@login_required
def student_edit(request, pk):
    """Editar alumno existente"""
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            # Registrar modificación de alumno en el log
            AuditLog.log_action(
                user=request.user,
                action='UPDATE',
                entity_type='STUDENT',
                entity_id=student.id,
                entity_name=str(student),
                description=f'Alumno modificado: {student.first_name} {student.last_name}',
                request=request
            )
            messages.success(request, f'Alumno {student} actualizado correctamente')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)

    return render(request, 'students/student_form.html', {'form': form, 'title': 'Editar Alumno', 'student': student})


@login_required
def student_delete(request, pk):
    """Eliminar alumno"""
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student_name = str(student)
        student_id = student.id
        # Registrar eliminación de alumno en el log antes de borrar
        AuditLog.log_action(
            user=request.user,
            action='DELETE',
            entity_type='STUDENT',
            entity_id=student_id,
            entity_name=student_name,
            description=f'Alumno eliminado: {student.first_name} {student.last_name} (DNI: {student.dni})',
            request=request
        )
        student.delete()
        messages.success(request, f'Alumno {student_name} eliminado correctamente')
        return redirect('student_list')

    return render(request, 'students/student_confirm_delete.html', {'student': student})


@login_required
def voucher_create(request, student_pk):
    """Añadir cargo/concepto a un alumno"""
    import json
    from decimal import Decimal

    student = get_object_or_404(Student, pk=student_pk)

    # Mapeo de tipos de concepto a duración en minutos
    PRACTICE_DURATION_MAP = {
        'PRACTICE_90': 90,
        'PRACTICE_60': 60,
        'PRACTICE_45': 45,
        'PRACTICE_30': 30,
    }

    if request.method == 'POST':
        form = VoucherForm(request.POST)
        if form.is_valid():
            concept_type = form.cleaned_data['concept_type']
            practice_date = form.cleaned_data.get('practice_date')

            # Si es una práctica individual, crear el registro de práctica Y el cargo
            if concept_type in PRACTICE_DURATION_MAP:
                duration = PRACTICE_DURATION_MAP[concept_type]
                practice_price = Voucher.CONCEPT_PRICES[concept_type]

                # Crear el cargo de la práctica individual
                voucher = Voucher.objects.create(
                    student=student,
                    concept_type=concept_type,
                    amount=practice_price,
                    description=f'Práctica {practice_date.strftime("%d/%m/%Y")}',
                    created_by=request.user
                )

                # Crear la práctica asociada al cargo
                practice = Practice.objects.create(
                    student=student,
                    duration=duration,
                    practice_date=practice_date,
                    notes=form.cleaned_data.get('description', ''),
                    is_billed=True,  # Ya está facturada con el cargo individual
                    billed_voucher=voucher,
                    created_by=request.user
                )

                # Registrar en auditoría
                AuditLog.log_action(
                    user=request.user,
                    action='CREATE',
                    entity_type='VOUCHER',
                    entity_id=voucher.id,
                    entity_name=f'Práctica {duration}\' - {student}',
                    description=f'Práctica de {duration} minutos ({practice_price}€) registrada para {student} (fecha: {practice_date})',
                    request=request
                )

                # Verificar si hay suficientes minutos para aplicar descuento de bono (450 min)
                # Contar minutos de prácticas del alumno que NO tienen descuento aplicado
                from django.db.models import Sum

                # Obtener todas las prácticas que cuentan para el bono (las individuales facturadas)
                practices_for_bonus = Practice.objects.filter(
                    student=student,
                    is_billed=True,
                    billed_voucher__concept_type__in=['PRACTICE_90', 'PRACTICE_60', 'PRACTICE_45', 'PRACTICE_30']
                )
                total_practice_minutes = practices_for_bonus.aggregate(total=Sum('duration'))['total'] or 0

                # Calcular cuántos bonos completos hay (cada 450 minutos)
                # Contar descuentos ya aplicados
                discounts_applied = Voucher.objects.filter(
                    student=student,
                    concept_type='BONUS_DISCOUNT'
                ).count()

                bonuses_earned = total_practice_minutes // 450
                bonuses_pending = bonuses_earned - discounts_applied

                if bonuses_pending > 0:
                    # Calcular el descuento: precio de 5 prácticas de 90' (5 x 65€ = 325€) - precio bono (300€) = 25€ de ahorro
                    # Pero ahora cobramos cada práctica, así que el descuento es la diferencia
                    # 5 prácticas de 90' = 325€, bono = 300€, descuento = 25€
                    discount_amount = Decimal('25.00')  # Descuento por alcanzar el bono

                    discount_voucher = Voucher.objects.create(
                        student=student,
                        concept_type='BONUS_DISCOUNT',
                        amount=-discount_amount,  # Importe negativo = descuento
                        description=f'Descuento por bono 450\' (prácticas acumuladas: {total_practice_minutes}\')',
                        created_by=request.user
                    )

                    # Registrar en auditoría
                    AuditLog.log_action(
                        user=request.user,
                        action='CREATE',
                        entity_type='VOUCHER',
                        entity_id=discount_voucher.id,
                        entity_name=f'Descuento Bono - {student}',
                        description=f'Descuento de {discount_amount}€ aplicado por alcanzar 450 minutos de prácticas',
                        request=request
                    )

                    messages.success(
                        request,
                        f'Práctica de {duration}\' ({practice_price}€) registrada. ¡Has alcanzado {total_practice_minutes}\' y se ha aplicado un descuento de {discount_amount}€!'
                    )
                else:
                    minutes_for_next_bonus = 450 - (total_practice_minutes % 450)
                    messages.success(
                        request,
                        f'Práctica de {duration}\' ({practice_price}€) registrada. Acumulados: {total_practice_minutes}\' (faltan {minutes_for_next_bonus}\' para el próximo descuento)'
                    )

                return redirect('student_detail', pk=student.pk)

            else:
                # Para conceptos que no son prácticas individuales, comportamiento normal
                voucher = form.save(commit=False)
                voucher.student = student
                voucher.created_by = request.user

                # Si no se especificó importe y no es "Otros", usar precio predefinido
                if not voucher.amount or voucher.amount == 0:
                    voucher.amount = Voucher.CONCEPT_PRICES.get(voucher.concept_type, 0)

                voucher.save()
                concept_name = voucher.get_concept_type_display()

                # Registrar creación de cargo en el log
                AuditLog.log_action(
                    user=request.user,
                    action='CREATE',
                    entity_type='VOUCHER',
                    entity_id=voucher.id,
                    entity_name=f'{concept_name} - {student}',
                    description=f'Cargo añadido: {concept_name} de {voucher.amount}€ para {student}',
                    request=request
                )
                messages.success(request, f'{concept_name} de {voucher.amount}€ añadido correctamente')
                return redirect('student_detail', pk=student.pk)
    else:
        form = VoucherForm()

    # Convertir precios a float para JSON (evitar problemas con Decimal y localización)
    concept_prices_json = {k: float(v) for k, v in Voucher.CONCEPT_PRICES.items()}

    # Calcular minutos pendientes para mostrar en el formulario
    unbilled_minutes = Practice.get_unbilled_minutes(student)

    # Pasar los precios al template para JavaScript
    context = {
        'form': form,
        'student': student,
        'concept_prices_json': json.dumps(concept_prices_json),
        'unbilled_minutes': unbilled_minutes,
        'minutes_for_bonus': max(0, 450 - unbilled_minutes),
    }
    return render(request, 'students/voucher_form.html', context)


@login_required
def payment_create(request, student_pk):
    """Registrar pago de un alumno"""
    student = get_object_or_404(Student, pk=student_pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.student = student
            payment.created_by = request.user
            payment.save()
            # Registrar creación de pago en el log
            payment_method_display = payment.get_payment_method_display()
            AuditLog.log_action(
                user=request.user,
                action='CREATE',
                entity_type='PAYMENT',
                entity_id=payment.id,
                entity_name=f'{payment_method_display} - {student}',
                description=f'Pago registrado: {payment.amount}€ ({payment_method_display}) para {student}',
                request=request
            )
            messages.success(request, f'Pago de {payment.amount}€ registrado correctamente')
            return redirect('student_detail', pk=student.pk)
    else:
        form = PaymentForm()

    return render(request, 'students/payment_form.html', {'form': form, 'student': student})


@login_required
def audit_log_list(request):
    """Vista para mostrar el historial de logs de auditoría"""
    logs = AuditLog.objects.all().order_by('-timestamp')

    # Filtros opcionales
    action_filter = request.GET.get('action', '')
    entity_filter = request.GET.get('entity_type', '')
    user_filter = request.GET.get('user', '')

    if action_filter:
        logs = logs.filter(action=action_filter)
    if entity_filter:
        logs = logs.filter(entity_type=entity_filter)
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)

    # Paginación (mostrar 50 logs por página)
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'action_filter': action_filter,
        'entity_filter': entity_filter,
        'user_filter': user_filter,
        'action_choices': AuditLog.ACTION_CHOICES,
        'entity_choices': AuditLog.ENTITY_CHOICES,
    }
    return render(request, 'students/audit_log_list.html', context)


def upload_receipt(request, token):
    """Vista pública para subir recibo (sin login requerido)"""
    from django.utils import timezone
    from django.http import HttpResponse

    # Buscar el pago por token
    payment = get_object_or_404(Payment, upload_token=token)

    if request.method == 'POST':
        # Verificar que se subió un archivo
        if 'receipt_file' not in request.FILES:
            messages.error(request, 'No se seleccionó ningún archivo.')
        else:
            receipt_file = request.FILES['receipt_file']

            # Validar tipo de archivo (solo imágenes y PDFs)
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf']
            if receipt_file.content_type not in allowed_types:
                messages.error(request, 'Solo se permiten archivos de imagen (JPG, PNG, GIF) o PDF.')
            elif receipt_file.size > 10 * 1024 * 1024:  # Máximo 10MB
                messages.error(request, 'El archivo es demasiado grande. Máximo 10MB.')
            else:
                # Guardar el archivo
                payment.receipt = receipt_file
                payment.receipt_uploaded_at = timezone.now()
                payment.save()

                messages.success(request, '¡Recibo subido correctamente!')

                # Mostrar página de éxito
                return render(request, 'students/upload_receipt_success.html', {
                    'payment': payment,
                })

    # Verificar si ya tiene recibo
    already_uploaded = payment.has_receipt()

    context = {
        'payment': payment,
        'already_uploaded': already_uploaded,
    }
    return render(request, 'students/upload_receipt.html', context)


def can_access_maintenance(user):
    """Verifica si el usuario puede acceder al módulo de mantenimiento"""
    # Solo usuarios 'david' o superusuarios pueden acceder
    return user.username == 'david' or user.is_superuser


@login_required
def vehicle_list(request):
    """Lista de vehículos"""
    if not can_access_maintenance(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('student_list')

    query = request.GET.get('q', '')
    vehicles = Vehicle.objects.all()

    if query:
        vehicles = vehicles.filter(
            Q(license_plate__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query)
        )

    context = {
        'vehicles': vehicles,
        'query': query,
    }
    return render(request, 'students/vehicle_list.html', context)


@login_required
def vehicle_create(request):
    """Crear nuevo vehículo"""
    if not can_access_maintenance(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('student_list')

    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.created_by = request.user
            vehicle.save()
            messages.success(request, f'Vehículo {vehicle.license_plate} creado correctamente')
            return redirect('vehicle_detail', pk=vehicle.pk)
    else:
        form = VehicleForm()

    return render(request, 'students/vehicle_form.html', {'form': form, 'title': 'Nuevo Vehículo'})


@login_required
def vehicle_detail(request, pk):
    """Detalle del vehículo con historial de mantenimientos"""
    if not can_access_maintenance(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('student_list')

    vehicle = get_object_or_404(Vehicle, pk=pk)
    maintenances = vehicle.maintenances.all()

    context = {
        'vehicle': vehicle,
        'maintenances': maintenances,
    }
    return render(request, 'students/vehicle_detail.html', context)


@login_required
def vehicle_edit(request, pk):
    """Editar vehículo existente"""
    if not can_access_maintenance(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('student_list')

    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vehículo {vehicle.license_plate} actualizado correctamente')
            return redirect('vehicle_detail', pk=vehicle.pk)
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'students/vehicle_form.html', {'form': form, 'title': 'Editar Vehículo', 'vehicle': vehicle})


@login_required
def vehicle_delete(request, pk):
    """Eliminar vehículo"""
    if not can_access_maintenance(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('student_list')

    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == 'POST':
        license_plate = vehicle.license_plate
        vehicle.delete()
        messages.success(request, f'Vehículo {license_plate} eliminado correctamente')
        return redirect('vehicle_list')

    return render(request, 'students/vehicle_confirm_delete.html', {'vehicle': vehicle})


@login_required
def maintenance_create(request, vehicle_pk):
    """Añadir mantenimiento a un vehículo"""
    if not can_access_maintenance(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('student_list')

    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)

    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.vehicle = vehicle
            maintenance.created_by = request.user
            maintenance.save()
            messages.success(request, f'Mantenimiento registrado correctamente')
            return redirect('vehicle_detail', pk=vehicle.pk)
    else:
        form = MaintenanceForm()

    return render(request, 'students/maintenance_form.html', {'form': form, 'vehicle': vehicle})


@login_required
def maintenance_edit(request, pk):
    """Editar mantenimiento existente"""
    if not can_access_maintenance(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('student_list')

    maintenance = get_object_or_404(Maintenance, pk=pk)
    vehicle = maintenance.vehicle

    if request.method == 'POST':
        form = MaintenanceForm(request.POST, instance=maintenance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mantenimiento actualizado correctamente')
            return redirect('vehicle_detail', pk=vehicle.pk)
    else:
        form = MaintenanceForm(instance=maintenance)

    return render(request, 'students/maintenance_form.html', {
        'form': form,
        'vehicle': vehicle,
        'editing': True,
        'maintenance': maintenance
    })


@login_required
def maintenance_delete(request, pk):
    """Eliminar mantenimiento"""
    if not can_access_maintenance(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('student_list')

    maintenance = get_object_or_404(Maintenance, pk=pk)
    vehicle_pk = maintenance.vehicle.pk

    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, 'Mantenimiento eliminado correctamente')
        return redirect('vehicle_detail', pk=vehicle_pk)

    return render(request, 'students/maintenance_confirm_delete.html', {'maintenance': maintenance})


# ==================== PRÁCTICAS ====================

@login_required
def practice_edit(request, pk):
    """Editar una práctica existente"""
    practice = get_object_or_404(Practice, pk=pk)
    student = practice.student

    # Solo bloquear edición si está en un bono agrupado (BONUS_5_PRACTICES)
    if practice.is_billed and practice.billed_voucher and practice.billed_voucher.concept_type == 'BONUS_5_PRACTICES':
        messages.error(request, 'No se puede editar una práctica que ya ha sido facturada en un bono agrupado.')
        return redirect('student_detail', pk=student.pk)

    if request.method == 'POST':
        form = PracticeForm(request.POST, instance=practice)
        if form.is_valid():
            old_duration = practice.duration
            new_duration = form.cleaned_data['duration']

            # Si cambió la duración y tiene cargo individual, actualizar el cargo
            if practice.billed_voucher and practice.billed_voucher.concept_type in ['PRACTICE_90', 'PRACTICE_60', 'PRACTICE_45', 'PRACTICE_30']:
                # Determinar el nuevo tipo de concepto según la duración
                duration_to_concept = {90: 'PRACTICE_90', 60: 'PRACTICE_60', 45: 'PRACTICE_45', 30: 'PRACTICE_30'}
                new_concept = duration_to_concept.get(new_duration)

                if new_concept:
                    voucher = practice.billed_voucher
                    voucher.concept_type = new_concept
                    voucher.amount = Voucher.CONCEPT_PRICES[new_concept]
                    voucher.description = f'Práctica {form.cleaned_data["practice_date"].strftime("%d/%m/%Y")}'
                    voucher.save()

            form.save()
            messages.success(request, 'Práctica actualizada correctamente')
            return redirect('student_detail', pk=student.pk)
    else:
        form = PracticeForm(instance=practice)

    unbilled_minutes = Practice.get_unbilled_minutes(student)

    return render(request, 'students/practice_form.html', {
        'form': form,
        'student': student,
        'unbilled_minutes': unbilled_minutes,
        'editing': True,
        'practice': practice
    })


@login_required
def practice_delete(request, pk):
    """Eliminar una práctica"""
    practice = get_object_or_404(Practice, pk=pk)
    student_pk = practice.student.pk

    # Solo bloquear eliminación si está en un bono agrupado (BONUS_5_PRACTICES)
    if practice.is_billed and practice.billed_voucher and practice.billed_voucher.concept_type == 'BONUS_5_PRACTICES':
        messages.error(request, 'No se puede eliminar una práctica que ya ha sido facturada en un bono agrupado.')
        return redirect('student_detail', pk=student_pk)

    if request.method == 'POST':
        # Si tiene cargo individual asociado, eliminarlo también
        if practice.billed_voucher and practice.billed_voucher.concept_type in ['PRACTICE_90', 'PRACTICE_60', 'PRACTICE_45', 'PRACTICE_30']:
            practice.billed_voucher.delete()

        practice.delete()
        messages.success(request, 'Práctica y cargo asociado eliminados correctamente')
        return redirect('student_detail', pk=student_pk)

    return render(request, 'students/practice_confirm_delete.html', {'practice': practice})


# ==================== FACTURAS ====================

@login_required
def generate_invoice_pdf(request, payment_pk):
    """Genera y descarga la factura en PDF para un pago con tarjeta"""
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    import io

    payment = get_object_or_404(Payment, pk=payment_pk)

    # Solo facturas para pagos con tarjeta
    if payment.payment_method != 'CARD':
        messages.error(request, 'Las facturas solo se generan para pagos con tarjeta.')
        return redirect('student_detail', pk=payment.student.pk)

    # Crear o recuperar la factura
    invoice = Invoice.create_from_payment(payment)

    # Crear el PDF en memoria
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CompanyName',
        fontSize=18,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#27ae60'),
        alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        name='InvoiceTitle',
        fontSize=24,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#333333'),
        alignment=TA_RIGHT
    ))
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#27ae60'),
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='Normal_Right',
        fontSize=10,
        alignment=TA_RIGHT
    ))

    elements = []

    # ===== CABECERA =====
    # Tabla con datos empresa a la izquierda y "FACTURA" a la derecha
    header_data = [
        [
            Paragraph(f"<b>{Invoice.COMPANY_NAME}</b>", styles['CompanyName']),
            Paragraph("FACTURA", styles['InvoiceTitle'])
        ],
        [
            Paragraph(f"CIF: {Invoice.COMPANY_CIF}<br/>{Invoice.COMPANY_ADDRESS}<br/>{Invoice.COMPANY_CITY}<br/>Tel: {Invoice.COMPANY_PHONE}<br/>{Invoice.COMPANY_EMAIL}", styles['Normal']),
            Paragraph(f"<b>Nº:</b> {invoice.invoice_number}<br/><b>Fecha:</b> {invoice.date_issued.strftime('%d/%m/%Y')}", styles['Normal_Right'])
        ]
    ]

    header_table = Table(header_data, colWidths=[10*cm, 7*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 1*cm))

    # ===== DATOS DEL CLIENTE =====
    elements.append(Paragraph("DATOS DEL CLIENTE", styles['SectionTitle']))

    client_data = [
        ['Nombre:', invoice.client_name],
        ['DNI:', invoice.client_dni],
    ]
    if invoice.client_address:
        client_data.append(['Dirección:', invoice.client_address])

    client_table = Table(client_data, colWidths=[3*cm, 14*cm])
    client_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 1*cm))

    # ===== DETALLE DE LA FACTURA =====
    elements.append(Paragraph("DETALLE", styles['SectionTitle']))

    detail_data = [
        ['Concepto', 'Base Imponible', f'IVA ({Invoice.IVA_RATE}%)', 'Total'],
        [invoice.concept, f'{invoice.base_amount:.2f} €', f'{invoice.iva_amount:.2f} €', f'{invoice.total_amount:.2f} €'],
    ]

    detail_table = Table(detail_data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm])
    detail_table.setStyle(TableStyle([
        # Cabecera
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Contenido
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 0.5*cm))

    # ===== TOTALES =====
    totals_data = [
        ['Base Imponible:', f'{invoice.base_amount:.2f} €'],
        [f'IVA ({Invoice.IVA_RATE}%):', f'{invoice.iva_amount:.2f} €'],
        ['TOTAL:', f'{invoice.total_amount:.2f} €'],
    ]

    totals_table = Table(totals_data, colWidths=[13*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 1.5*cm))

    # ===== MÉTODO DE PAGO =====
    elements.append(Paragraph("INFORMACIÓN DE PAGO", styles['SectionTitle']))
    elements.append(Paragraph(f"<b>Método de pago:</b> Tarjeta", styles['Normal']))
    elements.append(Paragraph(f"<b>Fecha de pago:</b> {payment.date_paid.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 2*cm))

    # ===== PIE =====
    footer_text = f"""
    <para align="center">
    <font size="8" color="#666666">
    {Invoice.COMPANY_NAME} - CIF: {Invoice.COMPANY_CIF}<br/>
    {Invoice.COMPANY_ADDRESS}, {Invoice.COMPANY_CITY}<br/>
    Este documento sirve como justificante de pago.
    </font>
    </para>
    """
    elements.append(Paragraph(footer_text, styles['Normal']))

    # Construir el PDF
    doc.build(elements)

    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{invoice.invoice_number}.pdf"'

    return response


# ==================== FACTURAS TRIMESTRALES ====================

@login_required
def tax_invoice_list(request):
    """Panel centralizado de facturas trimestrales"""
    from django.core.paginator import Paginator

    invoices = TaxInvoice.objects.all().select_related('student')

    # Filtros
    year_filter = request.GET.get('year', '')
    quarter_filter = request.GET.get('quarter', '')
    student_filter = request.GET.get('student', '')

    if year_filter:
        invoices = invoices.filter(year=year_filter)
    if quarter_filter:
        invoices = invoices.filter(quarter=quarter_filter)
    if student_filter:
        invoices = invoices.filter(
            Q(client_name__icontains=student_filter) |
            Q(client_dni__icontains=student_filter)
        )

    # Obtener anos disponibles para el filtro
    available_years = TaxInvoice.objects.values_list('year', flat=True).distinct().order_by('-year')

    paginator = Paginator(invoices, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'year_filter': year_filter,
        'quarter_filter': quarter_filter,
        'student_filter': student_filter,
        'available_years': available_years,
    }
    return render(request, 'students/tax_invoice_list.html', context)


@login_required
def tax_invoice_create(request, student_pk=None):
    """Crear una nueva factura trimestral"""
    from decimal import Decimal
    from datetime import date

    student = None
    if student_pk:
        student = get_object_or_404(Student, pk=student_pk)

    if request.method == 'POST':
        form = TaxInvoiceForm(request.POST, student=student)
        if form.is_valid():
            tax_invoice = form.save(commit=False)

            # Obtener o seleccionar alumno
            if student:
                tax_invoice.student = student
            else:
                # Caso de crear desde panel centralizado
                student_id = request.POST.get('student_id')
                if student_id:
                    tax_invoice.student = get_object_or_404(Student, pk=student_id)
                    student = tax_invoice.student

            # Generar numero de factura
            year = tax_invoice.fecha.year if tax_invoice.fecha else date.today().year
            tax_invoice.year = year
            tax_invoice.invoice_number = TaxInvoice.generate_invoice_number(year)

            # Snapshot de datos del cliente
            tax_invoice.client_name = f"{tax_invoice.student.first_name} {tax_invoice.student.last_name}"
            tax_invoice.client_dni = tax_invoice.student.dni
            tax_invoice.client_street = tax_invoice.student.street_address or tax_invoice.student.address
            tax_invoice.client_postal_code = tax_invoice.student.postal_code
            tax_invoice.client_municipality = tax_invoice.student.municipality
            tax_invoice.client_province = tax_invoice.student.province

            # Calcular importes
            total_paid = form.cleaned_data['total_paid']
            base, iva, tasas, total = TaxInvoice.compute_components(
                total_paid,
                tax_invoice.has_tasa_basica,
                tax_invoice.has_tasa_a,
                tax_invoice.has_traslado,
                tax_invoice.renovaciones_count,
                tax_invoice.curso
            )

            tax_invoice.base_imponible = base
            tax_invoice.iva_amount = iva
            tax_invoice.tasas_amount = tasas
            tax_invoice.total = total
            tax_invoice.created_by = request.user

            tax_invoice.save()

            # Vincular pagos seleccionados
            selected_payments = form.cleaned_data.get('selected_payments')
            if selected_payments:
                tax_invoice.payments.set(selected_payments)

            messages.success(request, f'Factura trimestral {tax_invoice.invoice_number} creada correctamente')

            if student_pk:
                return redirect('student_detail', pk=student_pk)
            return redirect('tax_invoice_list')
    else:
        form = TaxInvoiceForm(student=student)

    # Lista de alumnos para seleccionar (solo si no hay alumno predefinido)
    students_list = None
    if not student:
        students_list = Student.objects.filter(is_active=True).order_by('last_name', 'first_name')

    context = {
        'form': form,
        'student': student,
        'students_list': students_list,
    }
    return render(request, 'students/tax_invoice_form.html', context)


@login_required
def tax_invoice_detail(request, pk):
    """Ver detalle de una factura trimestral"""
    tax_invoice = get_object_or_404(TaxInvoice, pk=pk)
    context = {
        'tax_invoice': tax_invoice,
    }
    return render(request, 'students/tax_invoice_detail.html', context)


@login_required
def generate_tax_invoice_pdf(request, pk):
    """Genera PDF para una factura trimestral (formato Carrasco)"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    import io
    import os

    tax_invoice = get_object_or_404(TaxInvoice, pk=pk)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Datos del emisor (David Carrasco)
    DATOS_EMISOR = {
        'nombre': 'David Carrasco Sanchez',
        'dni': '52648389 D',
        'domicilio': 'C/ Beniparrell, 31 - Bajo 9',
        'cp': '46470',
        'municipio': 'Albal (Valencia)'
    }

    margin_left = 20 * mm
    margin_right = width - 20 * mm
    y = height - 20 * mm

    # === CABECERA ===
    # Intentar cargar logo
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'students', 'logo.png')
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, margin_left, y - 45 * mm, width=60 * mm, height=45 * mm, preserveAspectRatio=True)
        except:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margin_left, y - 5 * mm, "A U T O E S C U E L A")
            c.setFont("Helvetica-Bold", 22)
            c.drawString(margin_left, y - 15 * mm, "CARRASCO")
    else:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin_left, y - 5 * mm, "A U T O E S C U E L A")
        c.setFont("Helvetica-Bold", 22)
        c.drawString(margin_left, y - 15 * mm, "CARRASCO")

    # Recuadro datos emisor (derecha)
    box_x = 105 * mm
    box_y = y - 45 * mm
    box_width = 85 * mm
    box_height = 43 * mm

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.rect(box_x, box_y, box_width, box_height)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(box_x + 3 * mm, box_y + box_height - 7 * mm,
                 f"Fecha: {tax_invoice.fecha.strftime('%d/%m/%Y')}")
    c.drawString(box_x + 3 * mm, box_y + box_height - 14 * mm,
                 f"Nombre: {DATOS_EMISOR['nombre']}")
    c.setFont("Helvetica", 9)
    c.drawString(box_x + 3 * mm, box_y + box_height - 20 * mm, DATOS_EMISOR['dni'])
    c.setFont("Helvetica-Bold", 9)
    c.drawString(box_x + 3 * mm, box_y + box_height - 27 * mm,
                 f"Domicilio: {DATOS_EMISOR['domicilio']}")
    c.drawString(box_x + 3 * mm, box_y + box_height - 33 * mm,
                 f"C.P: {DATOS_EMISOR['cp']}")
    c.setFont("Helvetica", 9)
    c.drawString(box_x + 3 * mm, box_y + box_height - 39 * mm, DATOS_EMISOR['municipio'])

    y = y - 55 * mm

    # === DATOS CLIENTE ===
    client_box_height = 40 * mm
    client_box_y = y - client_box_height
    c.rect(margin_left, client_box_y, 80 * mm, client_box_height)

    c.setFont("Helvetica-BoldOblique", 9)
    c.drawString(margin_left + 3 * mm, y - 6 * mm, f"Cliente: {tax_invoice.client_name}")
    c.drawString(margin_left + 3 * mm, y - 12 * mm, f"Dni: {tax_invoice.client_dni}")
    c.drawString(margin_left + 3 * mm, y - 18 * mm, f"Domicilio: {tax_invoice.client_street}")
    c.drawString(margin_left + 3 * mm, y - 24 * mm, f"C.P: {tax_invoice.client_postal_code}")

    mun_prov = f"{tax_invoice.client_municipality}"
    if tax_invoice.client_province:
        mun_prov += f", {tax_invoice.client_province}"
    c.drawString(margin_left + 3 * mm, y - 30 * mm, f"Municipio/Provincia: {mun_prov}")

    c.setFont("Helvetica", 9)
    c.drawString(margin_left + 3 * mm, y - 38 * mm,
                 f"N FACTURA ALB {tax_invoice.invoice_number}")

    y = y - 50 * mm

    # === TABLA DE CONCEPTOS ===
    conceptos = []

    if tax_invoice.base_imponible > 0:
        concepto_curso = f"CURSO PERMISO {tax_invoice.curso}\nALUMNO: {tax_invoice.client_name},\n{tax_invoice.client_dni}"
        conceptos.append(['1', concepto_curso, f"{tax_invoice.base_imponible:.2f}", ''])

    if tax_invoice.tasas_amount > 0:
        conceptos.append(['1', "TASA DE TRAFICO (EXENTA DE IVA)", f"{tax_invoice.tasas_amount:.2f}", ''])

    table_data = [['CANTIDAD', 'CONCEPTO', 'PRECIO', 'TOTAL']]
    table_data.extend(conceptos)

    while len(table_data) < 12:
        table_data.append(['', '', '', ''])

    col_widths = [20 * mm, 95 * mm, 25 * mm, 25 * mm]
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    table_width, table_height = table.wrap(0, 0)
    table.drawOn(c, margin_left, y - table_height)

    y = y - table_height - 10 * mm

    # === TOTALES ===
    iva_percent = 21 if tax_invoice.iva_amount > 0 else 0

    totals_data = [
        ['BASE IMPONIBLE', f"{tax_invoice.base_imponible:.2f}"],
        [f'IVA {iva_percent} %', f"{tax_invoice.iva_amount:.2f}"],
        ['EXENTO', f"{tax_invoice.tasas_amount:.2f}"],
        ['TOTAL', f"{tax_invoice.total:.0f}"],
    ]

    totals_table = Table(totals_data, colWidths=[35 * mm, 20 * mm])
    totals_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    tw, th = totals_table.wrap(0, 0)
    totals_table.drawOn(c, margin_right - tw, y - th)

    c.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    num_short = tax_invoice.invoice_number.split('/')[1] if '/' in tax_invoice.invoice_number else tax_invoice.invoice_number
    response['Content-Disposition'] = f'attachment; filename="fra {num_short}.pdf"'

    return response
