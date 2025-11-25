from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Crea el usuario david para gestion de mantenimiento si no existe'

    def handle(self, *args, **options):
        username = 'david'
        password = '.david'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'El usuario "{username}" ya existe.'))
            return

        User.objects.create_user(
            username=username,
            password=password
        )

        self.stdout.write(self.style.SUCCESS(f'Usuario "{username}" creado correctamente.'))
