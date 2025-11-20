# Historial de Cambios - Autoescuela Carrasco

## [1.2.1] - Noviembre 2025

### 🔧 Cambios
- **Actualización de Precios de Conceptos**
  - Renovación de carnet: 10€ → 180€
  - Examen práctico: 20€ → 40€
  - Inscripción: 40€ → 300€
  - Práctica 90': 50€ → 65€
  - Práctica 60': 60€ → 43.33€
  - Práctica 45': 70€ → 32.50€
  - Práctica 30': 80€ (sin cambios)

- **Nuevo Concepto Añadido**
  - Bono 5 Prácticas 90': 300€

---

## [1.2.0] - Noviembre 2025

### ✨ Nuevas Características
- **Sistema Completo de Auditoría**
  - Nuevo modelo AuditLog para registrar todas las acciones del sistema
  - Tracking de: Creación, Modificación, Eliminación, Login, Logout
  - Registro automático de usuario, timestamp, dirección IP
  - Tipos de entidades: Alumno, Cargo, Pago, Usuario
  - Vista de historial con filtros por acción, entidad y usuario
  - Paginación de 50 registros por página
  - Link "Historial" en la barra de navegación

### 🗄️ Base de Datos
- **Migración 0003 aplicada**
  - Añadido campo `created_by` al modelo Student (ForeignKey a User)
  - Añadido campo `created_by` al modelo Voucher (ForeignKey a User)
  - Creado modelo AuditLog con 9 campos:
    - user (ForeignKey), action (CharField), entity_type (CharField)
    - entity_id (IntegerField), entity_name (CharField)
    - description (TextField), timestamp (DateTimeField)
    - ip_address (GenericIPAddressField)
  - Índices para mejorar rendimiento en consultas

### 🔧 Cambios Internos
- **Modelo AuditLog (students/models.py)**
  - Método estático `log_action()` para registrar logs fácilmente
  - Extracción automática de IP desde request headers
  - Opciones de Meta: ordering por timestamp descendente
- **Vistas actualizadas (students/views.py)**
  - user_login: Registra inicio de sesión
  - user_logout: Registra cierre de sesión
  - student_create: Registra creación de alumno + asigna created_by
  - student_edit: Registra modificación de alumno
  - student_delete: Registra eliminación antes de borrar
  - voucher_create: Registra creación de cargo + asigna created_by
  - payment_create: Ya tenía created_by, ahora registra el log
  - Nueva vista audit_log_list: Muestra historial con filtros
- **Admin (students/admin.py)**
  - AuditLog registrado con campos de solo lectura
  - Prohibida creación manual de logs
  - Solo superusuarios pueden eliminar logs

### 🎨 Interfaz
- **Template audit_log_list.html nuevo**
  - Tabla con columnas: Fecha, Usuario, Acción, Tipo, Entidad, Descripción, IP
  - Badges de colores según acción:
    - Verde: Creación
    - Amarillo: Modificación
    - Rojo: Eliminación
    - Azul: Login
    - Gris: Logout
  - Filtros por acción, tipo de entidad y usuario
  - Paginación completa con Primera/Anterior/Siguiente/Última
  - Contador total de registros
- **base.html actualizado**
  - Añadido link "Historial" en navbar (icono reloj)

### 🧪 Verificación
- Sistema de auditoría completamente funcional
- Logs se crean automáticamente en todas las operaciones CRUD
- Vista de historial accesible desde navbar
- Filtros funcionando correctamente
- Paginación operativa
- Servidor corriendo sin errores

---

## [1.1.0] - Noviembre 2025

### ✨ Nuevas Características
- **Sistema de Cargos con Conceptos Predefinidos**
  - Reemplazado sistema de "Bonos" por sistema flexible de "Cargos"
  - Añadidas 9 opciones predefinidas de conceptos:
    - Renovación de carnet (10€)
    - Examen práctico (20€)
    - Examen teórico (30€)
    - Inscripción (40€)
    - Práctica 90' (50€)
    - Práctica 60' (60€)
    - Práctica 45' (70€)
    - Práctica 30' (80€)
    - Otros (importe manual)
  - Selector desplegable con actualización automática de precios
  - JavaScript para bloquear/desbloquear campo de importe según selección
  - Campo de descripción opcional para todos los conceptos

### 🗄️ Base de Datos
- **Migración 0002 aplicada**
  - Añadido campo `concept_type` al modelo Voucher
  - Campo `amount` sin valor por defecto (asignado automáticamente)
  - Campo `description` ahora opcional (blank=True)
  - Actualizado verbose_name de "Bono" a "Cargo"

### 🎨 Interfaz
- **Template voucher_form.html completamente rediseñado**
  - Selector desplegable de conceptos con 9 opciones
  - Precio se actualiza automáticamente al cambiar concepto
  - Campo de importe bloqueado para conceptos predefinidos
  - Campo de importe editable solo para "Otros"
  - Hints dinámicos que muestran el precio predefinido
- **Template student_detail.html actualizado**
  - "Total en Bonos" → "Total en Cargos"
  - "Añadir Bono" → "Añadir Cargo"
  - Tabla ampliada con columnas: Fecha, Concepto, Descripción, Importe
  - Badge visual para mostrar el tipo de concepto
  - Iconos actualizados (clipboard-check, clipboard-plus-fill)

### 🔧 Cambios Internos
- **Modelo Voucher (students/models.py)**
  - Añadido `CONCEPT_CHOICES` con 9 opciones
  - Añadido `CONCEPT_PRICES` diccionario con precios predefinidos
  - Añadido campo `concept_type` (CharField con choices)
  - Método `save()` asigna precio automáticamente si no se especifica
- **Formulario VoucherForm (students/forms.py)**
  - Añadido campo `concept_type` con widget Select
  - Evento `onchange` para JavaScript
  - Labels actualizados: "Concepto", "Importe (€)"
- **Vista voucher_create (students/views.py)**
  - Lógica para asignar precio predefinido según concepto
  - Context con `concept_prices` para el template
  - Mensaje de éxito muestra nombre del concepto seleccionado

### 🧪 Verificación
- Sistema probado y funcionando correctamente
- `python manage.py check` sin issues
- Migración aplicada exitosamente
- Servidor iniciado sin errores

---

## [1.0.1] - Noviembre 2025

### 🐛 Correcciones
- **Error crítico de codificación UTF-8 resuelto**
  - Problema: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xac in position 2463`
  - Causa: Símbolos de euro (€) mal codificados en templates HTML
  - Archivos corregidos:
    - `students/templates/students/student_detail.html` (6 símbolos €)
    - `students/templates/students/payment_form.html` (2 símbolos €)
    - `students/templates/students/voucher_form.html` (1 símbolo €)
  - Estado: ✅ RESUELTO - Todos los archivos HTML ahora usan UTF-8 válido

### 📝 Documentación
- Creado `LEEME_CLAUDE.md` - Guía rápida para Claude Code con contexto del proyecto
- Creado `CONTEXTO_PROYECTO.md` - Documentación técnica completa e historial
- Actualizado `README.md` con:
  - Estructura detallada del proyecto
  - Información de los modelos de datos
  - Rutas del sistema
  - Configuración Django
  - Sección de solución de problemas con el error UTF-8
- Añadidos docstrings detallados a:
  - `students/models.py` - Descripción de los 4 modelos y sus relaciones
  - `students/views.py` - Descripción de las 9 vistas principales
  - `students/templates/students/base.html` - Comentario HTML descriptivo

### 🧪 Verificación
- Servidor probado con éxito en puerto 8080
- Login funcionando correctamente (admin/admin123)
- Redirección a `/students/` sin errores
- Página de lista de estudiantes carga correctamente (HTTP 200)
- Codificación UTF-8 verificada en todos los templates HTML

---

## [1.0.0] - Noviembre 2025 (Inicial)

### ✨ Características Iniciales
- Sistema completo de gestión de alumnos
- CRUD de alumnos (Crear, Leer, Actualizar, Eliminar)
- Sistema de bonos de prácticas (50€ default)
- Registro de pagos (efectivo/tarjeta)
- Cálculo automático de resumen financiero
- Búsqueda de alumnos por nombre, DNI o teléfono
- Sistema de autenticación con login/logout
- Panel de administración Django
- Diseño responsive con Bootstrap 5.3
- Colores corporativos AVAE (verde #2ecc71)

### 🗄️ Base de Datos
- 4 modelos implementados:
  - LicenseType (Tipos de carnet)
  - Student (Alumno principal)
  - Voucher (Bonos)
  - Payment (Pagos)
- Base de datos SQLite3
- Migración inicial aplicada

### 🎨 Interfaz
- 8 templates HTML con Bootstrap 5
- Navbar con autenticación
- Sistema de mensajes de Django
- Iconos Bootstrap Icons 1.11.0
- Footer corporativo

### 🔐 Seguridad
- Todas las vistas requieren login (@login_required)
- CSRF protection en formularios
- Usuario admin preconfigurado

---

## Formato del Changelog

Este archivo sigue [Semantic Versioning](https://semver.org/) y las convenciones de [Keep a Changelog](https://keepachangelog.com/).

**Tipos de cambios**:
- ✨ **Características**: Nuevas funcionalidades
- 🐛 **Correcciones**: Bugs arreglados
- 📝 **Documentación**: Cambios en documentación
- 🎨 **Estilo**: Cambios de formato/UI
- ♻️ **Refactorización**: Cambios de código sin afectar funcionalidad
- 🔒 **Seguridad**: Correcciones de seguridad
- 🧪 **Testing**: Añadir o corregir tests
