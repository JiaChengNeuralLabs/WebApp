"""
Vistas para Autoescuela Carrasco - Sistema de Gestión de Alumnos

Este archivo contiene 9 vistas principales:
1. user_login - Login (sin @login_required)
2. user_logout - Logout
3. student_list - Lista de alumnos con búsqueda por nombre/DNI/teléfono
4. student_create - Crear nuevo alumno
5. student_detail - Detalle del alumno con resumen financiero completo
6. student_edit - Editar alumno existente
7. student_delete - Eliminar alumno (con confirmación)
8. voucher_create - Añadir bono de prácticas al alumno
9. payment_create - Registrar pago del alumno

Todas las vistas excepto login/logout requieren autenticación (@login_required).
Los pagos se registran con el usuario que los creó (created_by).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Student, LicenseType, Voucher, Payment, AuditLog
from .forms import StudentForm, VoucherForm, PaymentForm


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
    student = get_object_or_404(Student, pk=pk)
    vouchers = student.vouchers.all()
    payments = student.payments.all()

    context = {
        'student': student,
        'vouchers': vouchers,
        'payments': payments,
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

    if request.method == 'POST':
        form = VoucherForm(request.POST)
        if form.is_valid():
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

    # Pasar los precios al template para JavaScript
    context = {
        'form': form,
        'student': student,
        'concept_prices_json': json.dumps(concept_prices_json)
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
