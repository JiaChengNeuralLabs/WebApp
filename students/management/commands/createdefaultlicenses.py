from django.core.management.base import BaseCommand
from students.models import LicenseType


class Command(BaseCommand):
    help = 'Crea los tipos de carnet por defecto si no existen'

    def handle(self, *args, **options):
        # Lista de tipos de carnet comunes en España
        license_types = [
            {'name': 'B', 'description': 'Automóviles y vehículos ligeros'},
            {'name': 'A', 'description': 'Motocicletas sin límite de cilindrada'},
            {'name': 'A1', 'description': 'Motocicletas hasta 125cc'},
            {'name': 'A2', 'description': 'Motocicletas hasta 35kW'},
            {'name': 'AM', 'description': 'Ciclomotores'},
            {'name': 'C', 'description': 'Camiones'},
            {'name': 'D', 'description': 'Autobuses'},
            {'name': 'BE', 'description': 'Turismo con remolque'},
        ]

        created_count = 0
        existing_count = 0

        for license_data in license_types:
            license_type, created = LicenseType.objects.get_or_create(
                name=license_data['name'],
                defaults={'description': license_data['description']}
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Creado tipo de carnet: {license_data["name"]}'))
            else:
                existing_count += 1

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'\nSe crearon {created_count} tipos de carnet.'))
        if existing_count > 0:
            self.stdout.write(self.style.WARNING(f'{existing_count} tipos de carnet ya existían.'))

        self.stdout.write(self.style.SUCCESS(f'\nTotal de tipos de carnet disponibles: {LicenseType.objects.count()}'))
