from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Crea un superusuario por defecto si no existe ninguno'

    def handle(self, *args, **options):
        # Verificar si ya existe algún superusuario
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING('Ya existe un superusuario. No se creará otro.'))
            return

        # Obtener credenciales de variables de entorno
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@autoescuela.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING('No se proporcionó DJANGO_SUPERUSER_PASSWORD. No se creará el superusuario.'))
            return

        # Crear el superusuario
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(self.style.SUCCESS(f'Superusuario "{username}" creado correctamente.'))
