"""
Comando para importar datos de direccion de alumnos desde archivos Excel Trimestre-X.xlsx

Uso:
    python manage.py import_trimestre C:\\path\\to\\Trimestre-1.xlsx
    python manage.py import_trimestre C:\\path\\to\\Trimestre-1.xlsx --dry-run

El comando solo actualiza campos de direccion (street_address, postal_code, municipality, province)
de alumnos que ya existen en la base de datos (busca por DNI).
NO crea alumnos nuevos.
"""

from django.core.management.base import BaseCommand, CommandError
from students.models import Student
from pathlib import Path


class Command(BaseCommand):
    help = 'Importa datos de direccion de alumnos desde un archivo Excel trimestral (Trimestre-X.xlsx)'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Ruta al archivo Excel')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular importacion sin guardar en la base de datos'
        )

    def normalize_dni(self, dni):
        """Normaliza el DNI para comparacion."""
        if not dni:
            return ''
        return str(dni).upper().replace(' ', '').replace('-', '').strip()

    def handle(self, *args, **options):
        try:
            from openpyxl import load_workbook
        except ImportError:
            raise CommandError('openpyxl es requerido. Instalar con: pip install openpyxl')

        excel_path = Path(options['excel_file'])
        dry_run = options['dry_run']

        if not excel_path.exists():
            raise CommandError(f'Archivo no encontrado: {excel_path}')

        self.stdout.write(f'Leyendo {excel_path.name}...')
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO SIMULACION - No se guardaran cambios'))

        wb = load_workbook(excel_path, read_only=True)
        ws = wb.active

        # Columnas esperadas (0-indexed):
        # 0: CURSO, 1: N FACTURA, 2: FECHA, 3: NOMBRE Y APELLIDOS, 4: DNI,
        # 5: BASE IMPONIBLE, 6: IVA, 7: TASAS, 8: TOTAL,
        # 9: DIRECCION, 10: CP, 11: MUNICIPIO, 12: PROVINCIA

        direcciones_dict = {}  # DNI -> datos de direccion

        for row_num in range(2, ws.max_row + 1):
            dni = ws.cell(row=row_num, column=5).value
            direccion = ws.cell(row=row_num, column=10).value
            cp = ws.cell(row=row_num, column=11).value
            municipio = ws.cell(row=row_num, column=12).value
            provincia = ws.cell(row=row_num, column=13).value

            if not dni:
                continue

            dni_clean = self.normalize_dni(dni)

            direccion_data = {
                'street_address': str(direccion).strip() if direccion else '',
                'postal_code': str(cp).strip() if cp else '',
                'municipality': str(municipio).strip() if municipio else '',
                'province': str(provincia).strip() if provincia else '',
            }

            # Guardar la mejor direccion (con mas campos llenos)
            if dni_clean not in direcciones_dict:
                direcciones_dict[dni_clean] = direccion_data
            else:
                # Actualizar con datos nuevos si tiene mas informacion
                existing = direcciones_dict[dni_clean]
                new_filled = sum(1 for v in direccion_data.values() if v)
                old_filled = sum(1 for v in existing.values() if v)
                if new_filled > old_filled:
                    direcciones_dict[dni_clean] = direccion_data

        wb.close()

        self.stdout.write(f'Encontradas {len(direcciones_dict)} direcciones unicas')
        self.stdout.write('')

        updated_count = 0
        not_found_count = 0
        skipped_count = 0

        for dni, data in direcciones_dict.items():
            # Buscar alumno por DNI
            try:
                student = Student.objects.get(dni__iexact=dni)

                # Verificar si hay algo que actualizar
                needs_update = False
                updates = []

                if not student.street_address and data['street_address']:
                    if not dry_run:
                        student.street_address = data['street_address']
                    updates.append(f"street_address='{data['street_address']}'")
                    needs_update = True

                if not student.postal_code and data['postal_code']:
                    if not dry_run:
                        student.postal_code = data['postal_code']
                    updates.append(f"postal_code='{data['postal_code']}'")
                    needs_update = True

                if not student.municipality and data['municipality']:
                    if not dry_run:
                        student.municipality = data['municipality']
                    updates.append(f"municipality='{data['municipality']}'")
                    needs_update = True

                if not student.province and data['province']:
                    if not dry_run:
                        student.province = data['province']
                    updates.append(f"province='{data['province']}'")
                    needs_update = True

                if needs_update:
                    if not dry_run:
                        student.save()
                    updated_count += 1
                    prefix = '[DRY] ' if dry_run else ''
                    self.stdout.write(self.style.SUCCESS(
                        f'  {prefix}Actualizado: {student.first_name} {student.last_name} ({dni})'
                    ))
                    for update in updates:
                        self.stdout.write(f'      -> {update}')
                else:
                    skipped_count += 1

            except Student.DoesNotExist:
                not_found_count += 1
                self.stdout.write(self.style.WARNING(
                    f'  No encontrado: DNI {dni}'
                ))
            except Student.MultipleObjectsReturned:
                self.stdout.write(self.style.ERROR(
                    f'  Error: Multiples alumnos con DNI {dni}'
                ))

        self.stdout.write('')
        self.stdout.write('-' * 50)
        self.stdout.write(self.style.SUCCESS(f'Actualizados: {updated_count}'))
        self.stdout.write(f'Sin cambios: {skipped_count}')
        if not_found_count:
            self.stdout.write(self.style.WARNING(f'No encontrados: {not_found_count}'))
        self.stdout.write('-' * 50)

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\nMODO SIMULACION - Ejecutar sin --dry-run para guardar cambios'
            ))
