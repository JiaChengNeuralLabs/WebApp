import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autoescuela.settings')
django.setup()

from django.contrib.auth.models import User
from students.models import LicenseType

# Establecer contraseña para admin
try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print("Contraseña del admin establecida correctamente")
except User.DoesNotExist:
    User.objects.create_superuser('admin', 'admin@autoescuelacarrasco.com', 'admin123')
    print("Superusuario admin creado")

# Crear tipos de carnet
license_types = [
    {'name': 'B', 'description': 'Carnet B - Automoviles'},
    {'name': 'A', 'description': 'Carnet A - Motocicletas'},
    {'name': 'A1', 'description': 'Carnet A1 - Motocicletas hasta 125cc'},
    {'name': 'A2', 'description': 'Carnet A2 - Motocicletas hasta 35kW'},
    {'name': 'C', 'description': 'Carnet C - Camiones'},
    {'name': 'D', 'description': 'Carnet D - Autobuses'},
]

for lt_data in license_types:
    LicenseType.objects.get_or_create(
        name=lt_data['name'],
        defaults={'description': lt_data['description']}
    )

print(f"Tipos de carnet creados: {LicenseType.objects.count()}")
print("\n=== Datos iniciales cargados ===")
print("Usuario: admin")
print("Contraseña: admin123")
print("URL: http://127.0.0.1:8000")
