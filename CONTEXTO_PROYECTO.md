# Contexto del Proyecto - Autoescuela Carrasco

## Información General
**Proyecto**: Sistema de gestión de alumnos para Autoescuela Carrasco (Franquicia AVAE)
**Propietario**: Jia Cheng
**Ubicación**: c:\Users\Jia.Cheng\Desktop\WebApp
**Tecnología**: Django 5.2.8 + Python 3.13 + Bootstrap 5 + SQLite
**Estado**: FUNCIONAL - Producción lista

## Propósito del Sistema
Gestionar alumnos de autoescuela con control financiero de bonos de prácticas y pagos.

### Funcionalidades principales:
1. **Gestión de alumnos** - CRUD completo (crear, leer, actualizar, eliminar)
2. **Sistema de bonos** - Registro de bonos de clases prácticas (50€ por defecto)
3. **Control de pagos** - Registro de pagos en efectivo o tarjeta
4. **Resumen financiero automático** - Cálculo de deuda, pagado y pendiente por alumno
5. **Búsqueda** - Por nombre, DNI o teléfono
6. **Autenticación** - Sistema de login obligatorio

## Credenciales de Acceso
- **Usuario**: admin
- **Contraseña**: admin123
- **Panel admin Django**: http://127.0.0.1:8000/admin (mismas credenciales)

## Arquitectura Técnica

### Modelos de Base de Datos (4 modelos)
```
LicenseType (Tipos de carnet)
  ↓ (ForeignKey)
Student (Alumno principal)
  ↓ (ForeignKey)
  ├─ Voucher (Bonos de prácticas)
  └─ Payment (Pagos realizados)
```

**Relaciones**:
- 1 LicenseType → N Students
- 1 Student → N Vouchers
- 1 Student → N Payments
- 1 User → N Payments (created_by)

### Vistas (8 vistas principales)
1. `user_login` - Login de usuario
2. `user_logout` - Logout
3. `student_list` - Lista con búsqueda (requiere login)
4. `student_create` - Crear alumno (requiere login)
5. `student_detail` - Detalle con resumen financiero (requiere login)
6. `student_edit` - Editar alumno (requiere login)
7. `student_delete` - Eliminar con confirmación (requiere login)
8. `voucher_create` - Añadir bono (requiere login)
9. `payment_create` - Registrar pago (requiere login)

### Templates HTML (8 archivos)
- `base.html` - Plantilla maestra con nav, Bootstrap 5, colores AVAE
- `login.html` - Página de inicio de sesión
- `student_list.html` - Lista de alumnos con búsqueda
- `student_detail.html` - Detalle con resumen financiero, bonos y pagos ⚠️ Contiene 6 símbolos €
- `student_form.html` - Formulario crear/editar alumno
- `student_confirm_delete.html` - Confirmación de eliminación
- `voucher_form.html` - Formulario añadir bono ⚠️ Contiene 1 símbolo €
- `payment_form.html` - Formulario registrar pago ⚠️ Contiene 2 símbolos €

## Historial de Problemas Resueltos

### 🔧 Error de Codificación UTF-8 (Resuelto - Nov 2025)
**Problema**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xac in position 2463: invalid start byte
```
Al hacer login y cargar `/students/`, Django no podía leer `student_detail.html`.

**Causa**:
Los archivos HTML contenían símbolos de euro (€) mal codificados. Tenían solo el byte `0xac`
en lugar de la secuencia UTF-8 completa `\xe2\x82\xac` (que representa €).

**Solución aplicada**:
Se corrigieron 3 archivos reemplazando los bytes mal formados con la codificación UTF-8 correcta:
- `students/templates/students/student_detail.html` - 6 símbolos € (líneas 57, 61, 66, 68, 108, 148)
- `students/templates/students/payment_form.html` - 2 símbolos € (líneas 26, 28)
- `students/templates/students/voucher_form.html` - 1 símbolo € (línea 34)

**Estado actual**: RESUELTO ✅
Todos los templates están ahora correctamente codificados en UTF-8 sin BOM.
Los símbolos € se muestran correctamente en el navegador.

## Cálculos Financieros (Lógica de negocio)

### Métodos del modelo Student:
```python
get_total_debt()        # Suma de todos los vouchers (bonos)
get_total_paid()        # Suma de todos los payments (pagos)
get_balance()           # total_paid - total_debt (puede ser negativo)
get_pending_amount()    # abs(balance) si balance < 0, sino 0
```

### Interpretación:
- **Total en Bonos** (deuda): Suma de todos los bonos añadidos al alumno
- **Total Pagado**: Suma de todos los pagos registrados
- **Pendiente de Pago**:
  - Si pagado < deuda → Muestra la diferencia (debe dinero)
  - Si pagado ≥ deuda → Muestra 0€ (está al día)

## Colores Corporativos AVAE
- **Verde principal**: #2ecc71 (botones principales, badges)
- **Verde oscuro**: #27ae60 (hover, navbar)
- **Blanco**: #ffffff (fondo)

Aplicados en `base.html` con CSS custom dentro de `<style>` tags.

## Comandos Útiles

### Iniciar servidor
```bash
# Activar entorno virtual
venv\Scripts\activate

# Iniciar servidor en puerto 8080
python manage.py runserver 8080

# O usar el script (doble clic)
start_server.bat
```

### Verificar estado
```bash
python manage.py check          # Verificar configuración
python manage.py showmigrations # Ver migraciones aplicadas
python manage.py shell          # Shell interactivo Django
```

### Base de datos
```bash
python manage.py makemigrations # Crear migraciones (si cambias models.py)
python manage.py migrate        # Aplicar migraciones
python manage.py createsuperuser # Crear nuevo admin
```

## Rutas del Sistema
```
URL                                      Vista                Template
─────────────────────────────────────────────────────────────────────────────
/students/login/                         user_login           login.html
/students/logout/                        user_logout          -
/students/                               student_list         student_list.html
/students/nuevo/                         student_create       student_form.html
/students/<pk>/                          student_detail       student_detail.html
/students/<pk>/editar/                   student_edit         student_form.html
/students/<pk>/eliminar/                 student_delete       student_confirm_delete.html
/students/<student_pk>/bono/nuevo/       voucher_create       voucher_form.html
/students/<student_pk>/pago/nuevo/       payment_create       payment_form.html
/admin/                                  (Django Admin)       -
```

## Notas Importantes para Claude Code

### Al abrir el proyecto en el futuro:
1. **Contexto rápido**: Este es un sistema Django funcional para gestión de autoescuela
2. **Archivos clave**:
   - `students/models.py` - Define la estructura de datos
   - `students/views.py` - Contiene la lógica de negocio
   - `students/templates/students/` - Plantillas HTML con Bootstrap
   - `db.sqlite3` - Base de datos (no modificar directamente)

3. **Codificación**: TODOS los archivos HTML están en UTF-8. Los símbolos € ya están corregidos.

4. **Testing**: Para probar cambios:
   ```bash
   python manage.py runserver 8080
   # Navegar a http://localhost:8080/students/login/
   # Login: admin / admin123
   ```

5. **Cambios seguros**:
   - ✅ Modificar templates HTML (mantener UTF-8)
   - ✅ Añadir campos a models.py (luego makemigrations + migrate)
   - ✅ Editar views.py para nueva lógica
   - ✅ Actualizar forms.py para nuevos campos
   - ⚠️ No tocar db.sqlite3 directamente
   - ⚠️ No modificar migraciones existentes

6. **Flujo de trabajo típico**:
   - Usuario pide cambio → Identificar archivos afectados → Leer archivos → Hacer cambios → Probar con runserver

## Estructura de Archivos Importantes
```
students/
├── models.py           # 4 modelos: LicenseType, Student, Voucher, Payment
├── views.py            # 9 funciones de vista (todas documentadas)
├── forms.py            # 3 formularios: StudentForm, VoucherForm, PaymentForm
├── urls.py             # 9 rutas definidas con name= para {% url %}
├── admin.py            # Configuración del panel admin
├── apps.py             # Configuración de la app
├── tests.py            # Tests (vacío por ahora)
└── templates/students/ # 8 templates HTML con Bootstrap 5
```

## Estado Actual del Proyecto
✅ **FUNCIONAL** - Sistema completamente operativo
✅ **ESTABLE** - No hay errores conocidos
✅ **UTF-8 CORREGIDO** - Todos los templates codificados correctamente
✅ **DOCUMENTADO** - README.md actualizado con información técnica completa

---

**Última actualización**: Noviembre 2025
**Última modificación**: Corrección de codificación UTF-8 en templates
**Versión**: 1.0 (Estable)
