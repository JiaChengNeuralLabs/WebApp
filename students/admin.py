from django.contrib import admin
from .models import LicenseType, Student, Voucher, Payment, AuditLog, TaxInvoice


@admin.register(LicenseType)
class LicenseTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'dni', 'phone', 'license_type', 'is_active', 'date_registered']
    list_filter = ['license_type', 'is_active', 'date_registered']
    search_fields = ['first_name', 'last_name', 'dni', 'phone']
    date_hierarchy = 'date_registered'


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'amount', 'date_created', 'description']
    list_filter = ['date_created']
    search_fields = ['student__first_name', 'student__last_name']
    date_hierarchy = 'date_created'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'amount', 'payment_method', 'date_paid', 'created_by']
    list_filter = ['payment_method', 'date_paid']
    search_fields = ['student__first_name', 'student__last_name']
    date_hierarchy = 'date_paid'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'entity_type', 'entity_name', 'ip_address']
    list_filter = ['action', 'entity_type', 'timestamp']
    search_fields = ['user__username', 'entity_name', 'description']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'action', 'entity_type', 'entity_id', 'entity_name', 'description', 'timestamp', 'ip_address']

    def has_add_permission(self, request):
        # No permitir añadir logs manualmente
        return False

    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar logs
        return request.user.is_superuser


@admin.register(TaxInvoice)
class TaxInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'fecha', 'client_name', 'curso', 'total', 'quarter', 'year']
    list_filter = ['year', 'quarter', 'curso', 'created_at']
    search_fields = ['invoice_number', 'client_name', 'client_dni']
    date_hierarchy = 'fecha'
    readonly_fields = ['created_at', 'created_by']

    fieldsets = (
        ('Identificacion', {
            'fields': ('invoice_number', 'fecha', 'quarter', 'year', 'curso')
        }),
        ('Cliente', {
            'fields': ('student', 'client_name', 'client_dni', 'client_street',
                      'client_postal_code', 'client_municipality', 'client_province')
        }),
        ('Tasas DGT', {
            'fields': ('has_tasa_basica', 'has_tasa_a', 'has_traslado', 'renovaciones_count')
        }),
        ('Importes', {
            'fields': ('base_imponible', 'iva_amount', 'tasas_amount', 'total')
        }),
        ('Metadata', {
            'fields': ('payments', 'notes', 'created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
