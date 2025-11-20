# Autoescuela Carrasco - Sistema de Gestión

Sistema web de gestión de alumnos para Autoescuela Carrasco (Franquicia AVAE).

## Características

- **Gestión de Alumnos**: Dar de alta, editar y eliminar alumnos con sus datos personales y tipo de carnet
- **Sistema de Bonos**: Añadir bonos de clases prácticas (50€ por defecto)
- **Registro de Pagos**: Registrar pagos en efectivo o tarjeta
- **Resumen Financiero**: Ver automáticamente cuánto debe cada alumno, cuánto ha pagado y el saldo pendiente
- **Búsqueda**: Buscar alumnos por nombre, DNI o teléfono
- **Autenticación**: Sistema de login con usuario y contraseña

## Instalación y Uso

### Primera vez

1. Abrir una terminal en la carpeta del proyecto
2. Activar el entorno virtual:
   ```
   venv\Scripts\activate
   ```
3. La base de datos y los datos iniciales ya están configurados

### Iniciar el servidor

1. Activar el entorno virtual (si no está activado):
   ```
   venv\Scripts\activate
   ```
2. Iniciar el servidor:
   ```
   python manage.py runserver
   ```
3. Abrir el navegador en: http://127.0.0.1:8000

### Credenciales de acceso

- **Usuario**: admin
- **Contraseña**: admin123

## Uso de la aplicación

### Crear un alumno

1. Iniciar sesión
2. Hacer clic en "Nuevo Alumno"
3. Rellenar los datos del alumno (nombre, apellidos, DNI, teléfono, tipo de carnet)
4. Guardar

### Añadir un bono

1. Ir a la página del alumno
2. Hacer clic en "Añadir Bono"
3. El importe por defecto es 50€, pero se puede cambiar
4. Guardar

### Registrar un pago

1. Ir a la página del alumno
2. Hacer clic en "Registrar Pago"
3. Introducir la cantidad pagada
4. Seleccionar el método de pago (Efectivo o Tarjeta)
5. Guardar

### Resumen financiero

En la página de cada alumno se muestra:
- **Total en Bonos**: Suma de todos los bonos añadidos
- **Total Pagado**: Suma de todos los pagos realizados
- **Pendiente de Pago**: Diferencia entre lo que debe y lo que ha pagado

## Tecnologías

- Python 3.13
- Django 5.2.8
- Bootstrap 5.3
- SQLite (base de datos)

## Colores corporativos AVAE

- Verde principal: #2ecc71
- Verde oscuro: #27ae60
- Blanco: #ffffff

## Estructura del proyecto

```
WebApp/
├── autoescuela/              # Configuración Django
│   ├── settings.py           # Configuración del proyecto
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # Punto de entrada WSGI
│
├── students/                 # App principal
│   ├── models.py             # Modelos: Student, LicenseType, Voucher, Payment
│   ├── views.py              # 8 vistas (login, CRUD alumnos, bonos, pagos)
│   ├── forms.py              # Formularios: StudentForm, VoucherForm, PaymentForm
│   ├── urls.py               # 9 rutas de la aplicación
│   ├── admin.py              # Configuración del admin de Django
│   ├── migrations/           # Migraciones de base de datos
│   └── templates/students/   # Plantillas HTML (8 archivos)
│       ├── base.html         # Plantilla base con Bootstrap 5
│       ├── login.html        # Página de login
│       ├── student_list.html # Lista de alumnos con búsqueda
│       ├── student_detail.html # Detalle con resumen financiero
│       ├── student_form.html # Crear/editar alumno
│       ├── student_confirm_delete.html
│       ├── voucher_form.html # Añadir bono (con símbolo €)
│       └── payment_form.html # Registrar pago (con símbolo €)
│
├── db.sqlite3                # Base de datos SQLite
├── manage.py                 # Script de gestión Django
├── start_server.bat          # Script para iniciar servidor (doble clic)
└── venv/                     # Entorno virtual Python
```

## Panel de administración

Puedes acceder al panel de administración de Django en:
http://127.0.0.1:8000/admin

Usa las mismas credenciales (admin/admin123)

## Información Técnica Detallada

### Modelos de Datos

**LicenseType** (Tipos de carnet)
- `name`: CharField - Nombre del carnet (B, A, A1, A2, C, D, etc.)
- `description`: TextField - Descripción del tipo de carnet

**Student** (Alumno) - Modelo principal
- `first_name`, `last_name`: CharField - Nombre y apellidos
- `dni`: CharField(unique) - DNI único del alumno
- `email`: EmailField (opcional)
- `phone`: CharField - Teléfono de contacto
- `address`: TextField (opcional)
- `license_type`: ForeignKey(LicenseType) - Tipo de carnet
- `date_registered`: DateTimeField(auto_now_add) - Fecha de alta
- `is_active`: BooleanField(default=True) - Estado activo/inactivo
- `notes`: TextField (opcional)
- Métodos: `get_total_debt()`, `get_total_paid()`, `get_balance()`, `get_pending_amount()`

**Voucher** (Bono de prácticas)
- `student`: ForeignKey(Student) - Alumno asociado
- `amount`: DecimalField(default=50.00) - Importe del bono
- `date_created`: DateTimeField(auto_now_add) - Fecha de creación
- `description`: TextField - Descripción del bono

**Payment** (Pago)
- `student`: ForeignKey(Student) - Alumno asociado
- `amount`: DecimalField - Cantidad pagada
- `payment_method`: CharField - 'CASH' (Efectivo) o 'CARD' (Tarjeta)
- `date_paid`: DateTimeField(auto_now_add) - Fecha del pago
- `notes`: TextField (opcional)
- `created_by`: ForeignKey(User) - Usuario que registró el pago

### Rutas (URLs)

```
/students/login/                              -> Login
/students/logout/                             -> Logout
/students/                                    -> Lista de alumnos (con búsqueda)
/students/nuevo/                              -> Crear alumno
/students/<int:pk>/                           -> Detalle del alumno
/students/<int:pk>/editar/                    -> Editar alumno
/students/<int:pk>/eliminar/                  -> Eliminar alumno
/students/<int:student_pk>/bono/nuevo/        -> Añadir bono
/students/<int:student_pk>/pago/nuevo/        -> Registrar pago
```

### Configuración Django

- **Versión**: Django 5.2.8, Python 3.13
- **Base de datos**: SQLite3 (db.sqlite3)
- **Idioma**: Español (es-es)
- **Zona horaria**: Europe/Madrid
- **Autenticación**:
  - LOGIN_URL = 'login'
  - LOGIN_REDIRECT_URL = 'student_list'
  - Todas las vistas requieren @login_required excepto login/logout

## Solución de Problemas

### Error de codificación UTF-8 (RESUELTO)
**Problema**: UnicodeDecodeError al cargar templates con símbolos € (euro)
**Solución**: Los archivos `student_detail.html`, `payment_form.html` y `voucher_form.html`
han sido corregidos con codificación UTF-8 válida. Los símbolos € están correctamente
codificados como bytes \xe2\x82\xac (UTF-8).

**Archivos corregidos**:
- students/templates/students/student_detail.html (6 símbolos €)
- students/templates/students/payment_form.html (2 símbolos €)
- students/templates/students/voucher_form.html (1 símbolo €)

### Notas importantes sobre codificación
- Todos los archivos HTML están en UTF-8 sin BOM
- Los símbolos de euro (€) están correctamente codificados
- Django lee los templates con codificación UTF-8 por defecto

### Verificar el servidor
Para asegurarte de que todo funciona:
1. Abre terminal en la carpeta del proyecto
2. Activa el entorno: venv\Scripts\activate
3. Ejecuta: python manage.py check
4. Si no hay errores, ejecuta: python manage.py runserver 8080
5. Abre http://localhost:8080/students/login/

