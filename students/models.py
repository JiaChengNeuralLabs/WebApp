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
import uuid


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
    expedition_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Número de expediente"
    )
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellidos")
    dni = models.CharField(max_length=20, unique=True, verbose_name="DNI")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    address = models.TextField(blank=True, verbose_name="Dirección")
    # Campos de dirección estructurados para facturas trimestrales
    street_address = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Calle/Dirección"
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Código Postal"
    )
    municipality = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Municipio"
    )
    province = models.CharField(
        max_length=100,
        blank=True,
        default='VALENCIA',
        verbose_name="Provincia"
    )
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
        ('BONUS_DISCOUNT', 'Descuento Bono 450\''),
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
        'BONUS_DISCOUNT': -25.00,  # Descuento por alcanzar 450 minutos
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
    # Campos para recibo
    receipt = models.FileField(
        upload_to='receipts/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Recibo"
    )
    upload_token = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Token de subida"
    )
    receipt_uploaded_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de subida del recibo"
    )

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-date_paid']

    def __str__(self):
        return f"Pago {self.id} - {self.student} - {self.amount}€ ({self.get_payment_method_display()})"

    def save(self, *args, **kwargs):
        # Generar token único si no existe
        if not self.upload_token:
            self.upload_token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def has_receipt(self):
        """Retorna True si el pago tiene recibo adjunto"""
        return bool(self.receipt)

    def get_upload_url(self):
        """Genera la URL pública para subir el recibo"""
        from django.urls import reverse
        return reverse('upload_receipt', kwargs={'token': self.upload_token})

    def get_whatsapp_url(self, phone_number, request=None):
        """Genera URL de WhatsApp con mensaje y enlace para subir recibo"""
        from django.conf import settings
        import urllib.parse

        # Construir URL completa del sitio
        if request:
            # Usar el host de la petición actual
            protocol = 'https' if request.is_secure() else 'http'
            base_url = f"{protocol}://{request.get_host()}"
        else:
            # Fallback: construir desde settings
            base_url = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'
            # Filtrar dominios genéricos como .onrender.com
            if base_url.startswith('.'):
                base_url = 'webapp-btp8.onrender.com'  # Usar el dominio específico
            if not base_url.startswith('http'):
                protocol = 'https' if not settings.DEBUG else 'http'
                base_url = f"{protocol}://{base_url}"

        upload_url = f"{base_url}{self.get_upload_url()}"

        # Mensaje para WhatsApp
        message = (
            f"📄 Subir recibo de pago\n"
            f"Alumno: {self.student.first_name} {self.student.last_name}\n"
            f"Cantidad: {self.amount}€\n"
            f"Enlace: {upload_url}"
        )

        # Formato internacional del número (sin + ni espacios)
        clean_phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')

        # URL de WhatsApp
        whatsapp_url = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(message)}"
        return whatsapp_url


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


class Vehicle(models.Model):
    """Modelo de Vehículo de la autoescuela"""
    license_plate = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Matrícula"
    )
    brand = models.CharField(max_length=50, verbose_name="Marca")
    model = models.CharField(max_length=50, verbose_name="Modelo")
    year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Año"
    )
    vehicle_type = models.CharField(
        max_length=20,
        choices=[
            ('CAR', 'Coche'),
            ('MOTORCYCLE', 'Moto'),
            ('TRUCK', 'Camión'),
            ('TRAILER', 'Tráiler'),
        ],
        default='CAR',
        verbose_name="Tipo de vehículo"
    )
    color = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Color"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    notes = models.TextField(blank=True, verbose_name="Notas")
    date_added = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de alta"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles_created',
        verbose_name="Creado por"
    )

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.license_plate} - {self.brand} {self.model}"

    def get_last_maintenance(self):
        """Retorna el último mantenimiento registrado"""
        return self.maintenances.first()

    def get_maintenance_count(self):
        """Retorna el número total de mantenimientos"""
        return self.maintenances.count()


class Maintenance(models.Model):
    """Modelo de Mantenimiento de vehículos"""
    MAINTENANCE_TYPES = [
        ('OIL_CHANGE', 'Cambio de aceite'),
        ('TIRE_CHANGE', 'Cambio de neumáticos'),
        ('BRAKE_CHECK', 'Revisión de frenos'),
        ('GENERAL_REVIEW', 'Revisión general'),
        ('ITV', 'ITV'),
        ('REPAIR', 'Reparación'),
        ('CLEANING', 'Limpieza'),
        ('FUEL', 'Combustible'),
        ('INSURANCE', 'Seguro'),
        ('OTHER', 'Otros'),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='maintenances',
        verbose_name="Vehículo"
    )
    maintenance_type = models.CharField(
        max_length=20,
        choices=MAINTENANCE_TYPES,
        verbose_name="Tipo de mantenimiento"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    brand = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Marca (repuesto/producto)"
    )
    model = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Modelo (repuesto/producto)"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Coste"
    )
    mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Kilometraje"
    )
    maintenance_date = models.DateField(
        default=timezone.now,
        verbose_name="Fecha de mantenimiento"
    )
    next_maintenance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Próximo mantenimiento"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenances_created',
        verbose_name="Registrado por"
    )
    date_created = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de registro"
    )

    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ['-maintenance_date', '-date_created']

    def __str__(self):
        return f"{self.get_maintenance_type_display()} - {self.vehicle.license_plate} - {self.maintenance_date}"


class Practice(models.Model):
    """Modelo de Práctica - Registro individual de cada clase práctica"""
    DURATION_CHOICES = [
        (90, 'Práctica 90 minutos'),
        (60, 'Práctica 60 minutos'),
        (45, 'Práctica 45 minutos'),
        (30, 'Práctica 30 minutos'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='practices',
        verbose_name="Alumno"
    )
    duration = models.PositiveIntegerField(
        choices=DURATION_CHOICES,
        default=90,
        verbose_name="Duración (minutos)"
    )
    practice_date = models.DateField(
        default=timezone.now,
        verbose_name="Fecha de la práctica"
    )
    notes = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Notas"
    )
    is_billed = models.BooleanField(
        default=False,
        verbose_name="Facturada en bono"
    )
    billed_voucher = models.ForeignKey(
        Voucher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='practices_included',
        verbose_name="Bono asociado"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='practices_created',
        verbose_name="Registrado por"
    )
    date_created = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de registro"
    )

    class Meta:
        verbose_name = "Práctica"
        verbose_name_plural = "Prácticas"
        ordering = ['-practice_date', '-date_created']

    def __str__(self):
        return f"{self.student} - {self.duration}' - {self.practice_date}"

    @staticmethod
    def get_unbilled_minutes(student):
        """Retorna el total de minutos no facturados del alumno"""
        from django.db.models import Sum
        result = Practice.objects.filter(
            student=student,
            is_billed=False
        ).aggregate(total=Sum('duration'))
        return result['total'] or 0

    @staticmethod
    def get_unbilled_practices(student):
        """Retorna las prácticas no facturadas del alumno"""
        return Practice.objects.filter(
            student=student,
            is_billed=False
        ).order_by('practice_date')


class Invoice(models.Model):
    """Modelo de Factura - Solo para pagos con tarjeta"""

    # Datos de la empresa (valores por defecto ficticios)
    COMPANY_NAME = "Autoescuela Carrasco"
    COMPANY_CIF = "B12345678"
    COMPANY_ADDRESS = "Calle Mayor, 15"
    COMPANY_CITY = "28001 Madrid"
    COMPANY_PHONE = "912 345 678"
    COMPANY_EMAIL = "info@autoescuelacarrasco.es"

    # IVA aplicable
    IVA_RATE = 21  # 21%

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='invoice',
        verbose_name="Pago"
    )
    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de factura"
    )
    date_issued = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de emisión"
    )
    # Datos del cliente en el momento de la factura
    client_name = models.CharField(
        max_length=200,
        verbose_name="Nombre del cliente"
    )
    client_dni = models.CharField(
        max_length=20,
        verbose_name="DNI del cliente"
    )
    client_address = models.TextField(
        blank=True,
        verbose_name="Dirección del cliente"
    )
    # Importes
    base_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Base imponible"
    )
    iva_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="IVA"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total"
    )
    # Concepto
    concept = models.CharField(
        max_length=200,
        verbose_name="Concepto"
    )

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-date_issued']

    def __str__(self):
        return f"Factura {self.invoice_number} - {self.client_name}"

    @staticmethod
    def generate_invoice_number():
        """Genera un número de factura único: AAAA-XXXXX"""
        from datetime import datetime
        year = datetime.now().year
        # Contar facturas del año actual
        count = Invoice.objects.filter(
            invoice_number__startswith=f"{year}-"
        ).count()
        return f"{year}-{str(count + 1).zfill(5)}"

    @classmethod
    def create_from_payment(cls, payment):
        """Crea una factura a partir de un pago con tarjeta"""
        from decimal import Decimal, ROUND_HALF_UP

        # Solo para pagos con tarjeta
        if payment.payment_method != 'CARD':
            return None

        # Verificar si ya existe factura
        if hasattr(payment, 'invoice'):
            return payment.invoice

        # Calcular importes (el pago incluye IVA)
        total = payment.amount
        # Base = Total / 1.21
        base = (total / Decimal('1.21')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        iva = total - base

        # Obtener concepto del último voucher o descripción genérica
        vouchers = payment.student.vouchers.filter(
            date_created__lte=payment.date_paid
        ).order_by('-date_created')

        if vouchers.exists():
            concept = f"Servicios de formación vial - {vouchers.first().get_concept_type_display()}"
        else:
            concept = "Servicios de formación vial"

        invoice = cls.objects.create(
            payment=payment,
            invoice_number=cls.generate_invoice_number(),
            client_name=f"{payment.student.first_name} {payment.student.last_name}",
            client_dni=payment.student.dni,
            client_address=payment.student.address or "",
            base_amount=base,
            iva_amount=iva,
            total_amount=total,
            concept=concept
        )
        return invoice


class TaxInvoice(models.Model):
    """
    Factura Trimestral con Tasas DGT.
    Diferente del modelo Invoice que es para recibos de pagos con tarjeta.
    TaxInvoice cubre uno o más pagos para reportes trimestrales.
    """
    from decimal import Decimal

    # Tipos de curso (matching Carrasco project)
    CURSO_CHOICES = [
        ('AM', 'AM - Ciclomotores'),
        ('A1', 'A1 - Motocicletas hasta 125cc'),
        ('A2', 'A2 - Motocicletas hasta 35kW'),
        ('A', 'A - Motocicletas sin límite'),
        ('B', 'B - Automóviles'),
        ('C', 'C - Camiones'),
        ('C+E', 'C+E - Camión con remolque'),
    ]

    # Constantes de tasas DGT (del proyecto Carrasco)
    TASA_BASICA = Decimal('94.05')
    TASA_A = Decimal('28.87')
    TRASLADO = Decimal('8.67')
    RENOVACION = Decimal('94.05')
    IVA_RATE = Decimal('0.21')

    # Relaciones principales
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name='tax_invoices',
        verbose_name="Alumno"
    )
    payments = models.ManyToManyField(
        Payment,
        related_name='tax_invoices',
        blank=True,
        verbose_name="Pagos incluidos"
    )

    # Identificación de factura
    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de factura"
    )  # Formato: YYYY/NNNN

    fecha = models.DateField(
        verbose_name="Fecha de factura"
    )
    quarter = models.PositiveSmallIntegerField(
        verbose_name="Trimestre",
        choices=[(1, 'T1'), (2, 'T2'), (3, 'T3'), (4, 'T4')]
    )
    year = models.PositiveIntegerField(
        verbose_name="Año fiscal"
    )

    # Tipo de curso
    curso = models.CharField(
        max_length=5,
        choices=CURSO_CHOICES,
        verbose_name="Tipo de curso"
    )

    # Flags de tasas (del invoice_gui.py de Carrasco)
    has_tasa_basica = models.BooleanField(
        default=False,
        verbose_name="Incluye Tasa Básica"
    )
    has_tasa_a = models.BooleanField(
        default=False,
        verbose_name="Incluye Tasa A (motocicletas)"
    )
    has_traslado = models.BooleanField(
        default=False,
        verbose_name="Incluye Traslado expediente"
    )
    renovaciones_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Número de renovaciones"
    )

    # Importes calculados (almacenados para auditoría)
    base_imponible = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Base imponible"
    )
    iva_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="IVA"
    )
    tasas_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Tasas DGT (exento)"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total factura"
    )

    # Snapshot de datos del cliente (para cumplimiento legal)
    client_name = models.CharField(max_length=200, verbose_name="Nombre cliente")
    client_dni = models.CharField(max_length=20, verbose_name="DNI cliente")
    client_street = models.CharField(max_length=200, blank=True, verbose_name="Dirección")
    client_postal_code = models.CharField(max_length=10, blank=True, verbose_name="CP")
    client_municipality = models.CharField(max_length=100, blank=True, verbose_name="Municipio")
    client_province = models.CharField(max_length=100, blank=True, verbose_name="Provincia")

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tax_invoices_created',
        verbose_name="Creado por"
    )
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Factura Trimestral"
        verbose_name_plural = "Facturas Trimestrales"
        ordering = ['-year', '-quarter', '-invoice_number']
        indexes = [
            models.Index(fields=['year', 'quarter']),
            models.Index(fields=['student', '-fecha']),
        ]

    def __str__(self):
        return f"Factura {self.invoice_number} - {self.client_name}"

    @staticmethod
    def get_quarter_from_date(date):
        """Retorna el trimestre (1-4) desde una fecha."""
        month = date.month
        if 1 <= month <= 3:
            return 1
        elif 4 <= month <= 6:
            return 2
        elif 7 <= month <= 9:
            return 3
        return 4

    @classmethod
    def generate_invoice_number(cls, year):
        """Genera el siguiente número de factura para el año: YYYY/NNNN"""
        last_invoice = cls.objects.filter(year=year).order_by('-invoice_number').first()
        if last_invoice:
            try:
                last_num = int(last_invoice.invoice_number.split('/')[1])
                next_num = last_num + 1
            except (IndexError, ValueError):
                next_num = 1
        else:
            next_num = 1
        return f"{year}/{next_num:04d}"

    @classmethod
    def compute_components(cls, total_paid, tasa_basica, tasa_a, traslado, renovaciones, curso):
        """
        Calcula el desglose de factura desde el total pagado.
        Adaptado de Carrasco invoice_gui.py compute_components()
        """
        from decimal import Decimal, ROUND_HALF_UP

        sum_tasas = (
            (1 if tasa_basica else 0) * cls.TASA_BASICA +
            (1 if tasa_a else 0) * cls.TASA_A +
            (1 if traslado else 0) * cls.TRASLADO +
            renovaciones * cls.RENOVACION
        )
        sum_tasas = sum_tasas.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        importe_after = total_paid - sum_tasas

        if importe_after <= 0:
            base = Decimal('0.00')
            iva = Decimal('0.00')
        else:
            # Cursos C y C+E están exentos de IVA
            if curso in ('C', 'C+E'):
                base = importe_after
                iva = Decimal('0.00')
            else:
                base = (importe_after / (1 + cls.IVA_RATE)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                iva = (base * cls.IVA_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        total = base + iva + sum_tasas
        return base, iva, sum_tasas, total

    def save(self, *args, **kwargs):
        # Auto-establecer trimestre y año desde fecha si no están establecidos
        if self.fecha:
            if not self.quarter:
                self.quarter = self.get_quarter_from_date(self.fecha)
            if not self.year:
                self.year = self.fecha.year
        super().save(*args, **kwargs)
