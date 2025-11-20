"""
Modelos de datos para Autoescuela Carrasco - Sistema de Gestión de Alumnos

Este archivo define 4 modelos principales:
- LicenseType: Tipos de carnet de conducir (B, A, A1, etc.)
- Student: Modelo principal de alumnos con datos personales
- Voucher: Bonos de clases prácticas (default 50€)
- Payment: Registro de pagos (efectivo o tarjeta)

El modelo Student incluye métodos para cálculo automático de:
- get_total_debt(): Suma total de bonos
- get_total_paid(): Suma total de pagos
- get_balance(): Diferencia entre pagos y deuda
- get_pending_amount(): Cantidad pendiente de pago

Relaciones: LicenseType → Student → (Voucher + Payment)
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class LicenseType(models.Model):
    """Tipos de carnet de conducir"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Tipo de Carnet"
        verbose_name_plural = "Tipos de Carnet"

    def __str__(self):
        return self.name


class Student(models.Model):
    """Modelo de Alumno"""
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellidos")
    dni = models.CharField(max_length=20, unique=True, verbose_name="DNI")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    address = models.TextField(blank=True, verbose_name="Dirección")
    license_type = models.ForeignKey(
        LicenseType,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Carnet"
    )
    date_registered = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Registro"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students_created',
        verbose_name="Creado por"
    )

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"
        ordering = ['-date_registered']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_total_debt(self):
        """Calcula el total que debe pagar el alumno"""
        total_vouchers = self.vouchers.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return total_vouchers

    def get_total_paid(self):
        """Calcula el total pagado por el alumno"""
        total_payments = self.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return total_payments

    def get_balance(self):
        """Calcula el saldo pendiente (negativo = debe, positivo = crédito)"""
        return self.get_total_paid() - self.get_total_debt()

    def get_pending_amount(self):
        """Devuelve cantidad pendiente de pago (0 si ha pagado todo o más)"""
        balance = self.get_balance()
        return abs(balance) if balance < 0 else 0


class Voucher(models.Model):
    """Modelo de Cargo/Concepto (anteriormente Bono)"""

    # Tipos de conceptos predefinidos con sus importes
    CONCEPT_CHOICES = [
        ('RENEWAL', 'Renovación de carnet'),
        ('PRACTICAL_EXAM', 'Examen práctico'),
        ('THEORY_EXAM', 'Examen teórico'),
        ('REGISTRATION', 'Inscripción'),
        ('PRACTICE_90', 'Práctica 90\''),
        ('PRACTICE_60', 'Práctica 60\''),
        ('PRACTICE_45', 'Práctica 45\''),
        ('PRACTICE_30', 'Práctica 30\''),
        ('BONUS_5_PRACTICES', 'Bono 5 Prácticas 90\''),
        ('OTHER', 'Otros'),
    ]

    # Importes predefinidos para cada concepto
    CONCEPT_PRICES = {
        'RENEWAL': 180.00,
        'PRACTICAL_EXAM': 40.00,
        'THEORY_EXAM': 30.00,
        'REGISTRATION': 300.00,
        'PRACTICE_90': 65.00,
        'PRACTICE_60': 43.33,
        'PRACTICE_45': 32.50,
        'PRACTICE_30': 80.00,
        'BONUS_5_PRACTICES': 300.00,
        'OTHER': 0.00,  # Para "Otros" el usuario ingresa el importe
    }

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='vouchers',
        verbose_name="Alumno"
    )
    concept_type = models.CharField(
        max_length=20,
        choices=CONCEPT_CHOICES,
        default='PRACTICE_90',
        verbose_name="Concepto"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Importe"
    )
    date_created = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Creación"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descripción adicional"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vouchers_created',
        verbose_name="Creado por"
    )

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.get_concept_type_display()} - {self.student} - {self.amount}€"

    def save(self, *args, **kwargs):
        # Si no se especifica importe y no es "Otros", usar el precio predefinido
        if not self.amount or self.amount == 0:
            self.amount = self.CONCEPT_PRICES.get(self.concept_type, 0)
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Modelo de Pago"""
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Efectivo'),
        ('CARD', 'Tarjeta'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Alumno"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Importe"
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Método de Pago"
    )
    date_paid = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Pago"
    )
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Registrado por"
    )

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-date_paid']

    def __str__(self):
        return f"Pago {self.id} - {self.student} - {self.amount}€ ({self.get_payment_method_display()})"


class AuditLog(models.Model):
    """Modelo de Auditoría - Registro de todas las acciones en el sistema"""

    ACTION_CHOICES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Modificación'),
        ('DELETE', 'Eliminación'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
    ]

    ENTITY_CHOICES = [
        ('STUDENT', 'Alumno'),
        ('VOUCHER', 'Cargo'),
        ('PAYMENT', 'Pago'),
        ('USER', 'Usuario'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuario",
        help_text="Usuario que realizó la acción"
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name="Acción"
    )
    entity_type = models.CharField(
        max_length=10,
        choices=ENTITY_CHOICES,
        verbose_name="Tipo de entidad"
    )
    entity_id = models.IntegerField(
        verbose_name="ID de entidad",
        help_text="ID del objeto afectado"
    )
    entity_name = models.CharField(
        max_length=200,
        verbose_name="Nombre de entidad",
        help_text="Nombre o descripción del objeto afectado"
    )
    description = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción detallada de la acción"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha y hora"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.get_entity_type_display()} - {self.user} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"

    @staticmethod
    def log_action(user, action, entity_type, entity_id, entity_name, description, request=None):
        """
        Helper para registrar acciones en el log de auditoría

        Args:
            user: Usuario que realiza la acción
            action: Tipo de acción ('CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT')
            entity_type: Tipo de entidad ('STUDENT', 'VOUCHER', 'PAYMENT', 'USER')
            entity_id: ID del objeto afectado
            entity_name: Nombre o descripción del objeto
            description: Descripción detallada de la acción
            request: Request HTTP (opcional, para obtener IP)
        """
        ip_address = None
        if request:
            # Obtener IP del usuario
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

        return AuditLog.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            ip_address=ip_address
        )
