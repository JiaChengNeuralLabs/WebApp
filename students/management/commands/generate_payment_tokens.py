from django.core.management.base import BaseCommand
from students.models import Payment
import uuid


class Command(BaseCommand):
    help = 'Genera tokens únicos para pagos que no tienen token'

    def handle(self, *args, **options):
        # Buscar pagos sin token
        payments_without_token = Payment.objects.filter(upload_token__isnull=True)
        count = payments_without_token.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('Todos los pagos ya tienen token.'))
            return

        self.stdout.write(f'Encontrados {count} pagos sin token.')

        # Generar tokens
        updated = 0
        for payment in payments_without_token:
            payment.upload_token = str(uuid.uuid4())
            payment.save()
            updated += 1
            self.stdout.write(self.style.SUCCESS(f'[OK] Token generado para pago #{payment.id}'))

        self.stdout.write(self.style.SUCCESS(f'\n{updated} pagos actualizados con tokens unicos.'))
