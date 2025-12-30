"""
Comando para importar alumnos y pagos desde archivos Excel Trimestre-X.xlsx

Uso:
    python manage.py import_trimestre C:\\path\\to\\Trimestre-1.xlsx
    python manage.py import_trimestre C:\\path\\to\\Trimestre-1.xlsx --dry-run

El comando:
1. Crea alumnos nuevos si no existen (busca por DNI)
2. Actualiza direccion de alumnos existentes si esta vacia
3. Registra pagos con el TOTAL de cada fila del Excel

Columnas esperadas del Excel:
    A: CURSO, B: N FACTURA, C: FECHA, D: NOMBRE Y APELLIDOS, E: DNI,
    F: BASE IMPONIBLE, G: IVA, H: TASAS, I: TOTAL,
    J: DIRECCION, K: CP, L: MUNICIPIO, M: PROVINCIA
"""

from django.core.management.base import BaseCommand, CommandError
from students.models import Student, Payment, LicenseType
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime


class Command(BaseCommand):
    help = 'Importa alumnos y pagos desde un archivo Excel trimestral (Trimestre-X.xlsx)'

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

    def parse_name(self, full_name):
        """Separa nombre completo en nombre y apellidos."""
        if not full_name:
            return '', ''

        full_name = str(full_name).strip()
        parts = full_name.split()

        if len(parts) == 0:
            return '', ''
        elif len(parts) == 1:
            return parts[0], ''
        elif len(parts) == 2:
            # Asumimos: APELLIDO NOMBRE o NOMBRE APELLIDO
            # En España es más común APELLIDOS NOMBRE, así que:
            return parts[1], parts[0]  # nombre, apellido
        elif len(parts) == 3:
            # APELLIDO1 APELLIDO2 NOMBRE
            return parts[2], f"{parts[0]} {parts[1]}"
        else:
            # APELLIDO1 APELLIDO2 NOMBRE1 NOMBRE2...
            return ' '.join(parts[2:]), f"{parts[0]} {parts[1]}"

    def parse_amount(self, value):
        """Convierte valor a Decimal."""
        if value is None:
            return Decimal('0.00')

        try:
            # Si es número, convertir directamente
            if isinstance(value, (int, float)):
                return Decimal(str(value)).quantize(Decimal('0.01'))

            # Si es string, limpiar y convertir
            value_str = str(value).strip()
            # Remover símbolo de euro y espacios
            value_str = value_str.replace('€', '').replace(' ', '')
            # Manejar formato español (1.234,56) vs inglés (1,234.56)
            if ',' in value_str and '.' in value_str:
                # Formato español: 1.234,56
                value_str = value_str.replace('.', '').replace(',', '.')
            elif ',' in value_str:
                # Solo coma: puede ser 1234,56 (español) o 1,234 (inglés miles)
                # Asumimos español si hay 2 decimales después de la coma
                parts = value_str.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    value_str = value_str.replace(',', '.')
                else:
                    value_str = value_str.replace(',', '')

            return Decimal(value_str).quantize(Decimal('0.01'))
        except (InvalidOperation, ValueError):
            return Decimal('0.00')

    def parse_date(self, value):
        """Convierte valor a fecha."""
        if value is None:
            return None

        # Si ya es datetime
        if isinstance(value, datetime):
            return value

        # Si es string, intentar parsear
        value_str = str(value).strip()

        # Formatos comunes
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d/%m/%y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value_str, fmt)
            except ValueError:
                continue

        return None

    def get_license_type(self, curso):
        """Obtiene o crea el tipo de carnet."""
        if not curso:
            curso = 'B'  # Default

        curso = str(curso).upper().strip()

        # Mapeo de cursos del Excel a tipos de carnet
        mapping = {
            'AM': 'AM',
            'A1': 'A1',
            'A2': 'A2',
            'A': 'A',
            'B': 'B',
            'C': 'C',
            'C+E': 'C+E',
            'CE': 'C+E',
        }

        license_name = mapping.get(curso, curso)

        license_type, created = LicenseType.objects.get_or_create(
            name=license_name,
            defaults={'description': f'Carnet tipo {license_name}'}
        )

        return license_type

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

        # Contadores
        students_created = 0
        students_updated = 0
        payments_created = 0
        payments_skipped = 0  # Pagos duplicados
        rows_skipped = 0

        # Columnas (1-indexed para openpyxl):
        # A(1): CURSO, B(2): N FACTURA, C(3): FECHA, D(4): NOMBRE Y APELLIDOS, E(5): DNI,
        # F(6): BASE IMPONIBLE, G(7): IVA, H(8): TASAS, I(9): TOTAL,
        # J(10): DIRECCION, K(11): CP, L(12): MUNICIPIO, M(13): PROVINCIA

        for row_num in range(2, ws.max_row + 1):
            curso = ws.cell(row=row_num, column=1).value
            n_factura = ws.cell(row=row_num, column=2).value
            fecha = ws.cell(row=row_num, column=3).value
            nombre_completo = ws.cell(row=row_num, column=4).value
            dni = ws.cell(row=row_num, column=5).value
            base_imponible = ws.cell(row=row_num, column=6).value
            iva = ws.cell(row=row_num, column=7).value
            tasas = ws.cell(row=row_num, column=8).value
            total = ws.cell(row=row_num, column=9).value
            direccion = ws.cell(row=row_num, column=10).value
            cp = ws.cell(row=row_num, column=11).value
            municipio = ws.cell(row=row_num, column=12).value
            provincia = ws.cell(row=row_num, column=13).value

            # Validar datos mínimos
            dni_clean = self.normalize_dni(dni)
            if not dni_clean:
                rows_skipped += 1
                continue

            # Parsear datos
            first_name, last_name = self.parse_name(nombre_completo)
            total_amount = self.parse_amount(total)
            fecha_parsed = self.parse_date(fecha)

            if not first_name and not last_name:
                self.stdout.write(self.style.WARNING(
                    f'  Fila {row_num}: Sin nombre para DNI {dni_clean}, saltando...'
                ))
                rows_skipped += 1
                continue

            # Buscar o crear alumno
            try:
                student = Student.objects.get(dni__iexact=dni_clean)
                is_new_student = False

                # Actualizar direccion si esta vacia
                updated_fields = []
                if not student.street_address and direccion:
                    student.street_address = str(direccion).strip()
                    updated_fields.append('direccion')
                if not student.postal_code and cp:
                    student.postal_code = str(cp).strip()
                    updated_fields.append('CP')
                if not student.municipality and municipio:
                    student.municipality = str(municipio).strip()
                    updated_fields.append('municipio')
                if not student.province and provincia:
                    student.province = str(provincia).strip()
                    updated_fields.append('provincia')

                if updated_fields and not dry_run:
                    student.save()
                    students_updated += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  Actualizado: {student} - {", ".join(updated_fields)}'
                    ))
                elif updated_fields and dry_run:
                    students_updated += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  [DRY] Actualizaria: {first_name} {last_name} - {", ".join(updated_fields)}'
                    ))

            except Student.DoesNotExist:
                # Crear alumno nuevo
                is_new_student = True
                license_type = self.get_license_type(curso)

                if not dry_run:
                    student = Student.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        dni=dni_clean,
                        phone='',  # No disponible en Excel
                        license_type=license_type,
                        street_address=str(direccion).strip() if direccion else '',
                        postal_code=str(cp).strip() if cp else '',
                        municipality=str(municipio).strip() if municipio else '',
                        province=str(provincia).strip() if provincia else 'VALENCIA',
                    )
                    students_created += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  Creado alumno: {student} ({dni_clean}) - {license_type.name}'
                    ))
                else:
                    students_created += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  [DRY] Crearia alumno: {first_name} {last_name} ({dni_clean})'
                    ))

            except Student.MultipleObjectsReturned:
                self.stdout.write(self.style.ERROR(
                    f'  Fila {row_num}: Multiples alumnos con DNI {dni_clean}'
                ))
                rows_skipped += 1
                continue

            # Registrar pago si hay importe
            if total_amount > 0:
                # Crear identificador único basado en número de factura o DNI+importe+fecha
                n_factura_str = str(n_factura).strip() if n_factura else None

                if not dry_run:
                    # Verificar duplicados de múltiples formas:
                    existing_payment = None

                    # 1. Buscar por número de factura en las notas (más fiable)
                    if n_factura_str:
                        existing_payment = Payment.objects.filter(
                            student=student,
                            notes__icontains=f'Factura {n_factura_str}'
                        ).first()

                    # 2. Si no hay número de factura, buscar por importe+fecha
                    if not existing_payment and fecha_parsed:
                        existing_payment = Payment.objects.filter(
                            student=student,
                            amount=total_amount,
                            date_paid__date=fecha_parsed.date() if hasattr(fecha_parsed, 'date') else fecha_parsed
                        ).first()

                    if not existing_payment:
                        payment = Payment.objects.create(
                            student=student,
                            amount=total_amount,
                            payment_method='CARD',  # Asumimos tarjeta para facturas trimestrales
                            date_paid=fecha_parsed or datetime.now(),
                            notes=f'Importado de {excel_path.name} - Factura {n_factura_str or "N/A"}'
                        )
                        payments_created += 1
                        self.stdout.write(f'    + Pago: {total_amount}€ - Factura {n_factura_str or "N/A"}')
                    else:
                        payments_skipped += 1
                        self.stdout.write(self.style.WARNING(
                            f'    = Pago ya existe: {total_amount}€ - Factura {n_factura_str or "N/A"}'
                        ))
                else:
                    payments_created += 1
                    self.stdout.write(f'    [DRY] + Pago: {total_amount}€ - Factura {n_factura_str or "N/A"}')

        wb.close()

        # Resumen
        self.stdout.write('')
        self.stdout.write('=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Alumnos creados: {students_created}'))
        self.stdout.write(self.style.SUCCESS(f'Alumnos actualizados: {students_updated}'))
        self.stdout.write(self.style.SUCCESS(f'Pagos registrados: {payments_created}'))
        if payments_skipped:
            self.stdout.write(f'Pagos duplicados (ignorados): {payments_skipped}')
        if rows_skipped:
            self.stdout.write(self.style.WARNING(f'Filas saltadas: {rows_skipped}'))
        self.stdout.write('=' * 50)

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\nMODO SIMULACION - Ejecutar sin --dry-run para guardar cambios'
            ))
