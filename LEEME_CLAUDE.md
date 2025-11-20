# 🤖 INFORMACIÓN PARA CLAUDE CODE

## ⚡ Contexto Rápido (Lee esto primero)

**¿Qué es esto?** Sistema Django de gestión de alumnos para Autoescuela Carrasco (Franquicia AVAE)
**Estado**: ✅ FUNCIONAL - Listo para producción
**Usuario**: Jia Cheng
**Ubicación**: `c:\Users\Jia.Cheng\Desktop\WebApp`

## 🎯 Propósito
Gestionar alumnos de autoescuela con:
- CRUD de alumnos (nombre, DNI, teléfono, carnet, etc.)
- Bonos de prácticas (50€ por defecto)
- Registro de pagos (efectivo/tarjeta)
- Cálculo automático de deuda vs pagado

## 🔑 Acceso Rápido
```
Usuario: admin
Password: admin123
URL: http://127.0.0.1:8000/students/login/
Admin: http://127.0.0.1:8000/admin
```

## 📁 Archivos Más Importantes

### Leer PRIMERO:
1. **CONTEXTO_PROYECTO.md** ← Contexto completo, historial de problemas
2. **README.md** ← Documentación técnica detallada
3. **students/models.py** ← 4 modelos: LicenseType, Student, Voucher, Payment
4. **students/views.py** ← 9 vistas con lógica de negocio

### Templates HTML (8 archivos en students/templates/students/):
- `base.html` - Plantilla maestra (Bootstrap 5, navbar, colores AVAE)
- `student_detail.html` - ⚠️ Contiene 6 símbolos € (UTF-8 corregido)
- `payment_form.html` - ⚠️ Contiene 2 símbolos € (UTF-8 corregido)
- `voucher_form.html` - ⚠️ Contiene 1 símbolo € (UTF-8 corregido)

## ⚠️ IMPORTANTE: Problema de Codificación (RESUELTO)

### Historia:
El usuario reportó este error al hacer login:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xac in position 2463
```

### Causa:
3 archivos HTML tenían símbolos € mal codificados (solo byte `0xac` en vez de `\xe2\x82\xac`)

### Solución Aplicada:
✅ `student_detail.html` - 6 símbolos € corregidos (líneas 57, 61, 66, 68, 108, 148)
✅ `payment_form.html` - 2 símbolos € corregidos (líneas 26, 28)
✅ `voucher_form.html` - 1 símbolo € corregido (línea 34)

### Estado Actual:
✅ Todos los archivos HTML están en UTF-8 sin BOM
✅ Los símbolos € funcionan correctamente
✅ El login y navegación funcionan sin errores

**NO REVERTIR ESTOS CAMBIOS** - Los símbolos € deben mantenerse como están.

## 🚀 Cómo Probar el Sistema

```bash
# 1. Activar entorno virtual
venv\Scripts\activate

# 2. Iniciar servidor
python manage.py runserver 8080

# 3. Abrir navegador
http://localhost:8080/students/login/

# 4. Login
Usuario: admin
Password: admin123
```

## 🏗️ Arquitectura Rápida

### Base de Datos (SQLite3):
```
LicenseType (Tipos de carnet: B, A, A1, etc.)
    ↓ ForeignKey
Student (Alumno principal)
    ↓ ForeignKey
    ├─ Voucher (Bonos de 50€)
    └─ Payment (Pagos efectivo/tarjeta)
```

### Rutas Principales:
```
/students/                          - Lista de alumnos
/students/nuevo/                    - Crear alumno
/students/<pk>/                     - Detalle + resumen financiero
/students/<pk>/editar/              - Editar alumno
/students/<pk>/eliminar/            - Eliminar alumno
/students/<pk>/bono/nuevo/          - Añadir bono
/students/<pk>/pago/nuevo/          - Registrar pago
```

### Cálculos Financieros (en Student model):
```python
get_total_debt()      # Suma de bonos
get_total_paid()      # Suma de pagos
get_balance()         # pagado - deuda
get_pending_amount()  # Cuánto debe (si balance < 0)
```

## 🎨 Diseño
- **Framework**: Bootstrap 5.3
- **Iconos**: Bootstrap Icons 1.11.0
- **Colores AVAE**: Verde #2ecc71, Verde oscuro #27ae60

## 📝 Si el Usuario Pide Cambios

### Workflow típico:
1. **Entender qué quiere cambiar**
2. **Leer los archivos relevantes** (usa Read tool)
3. **Hacer los cambios** (usa Edit tool, NO Write si existe)
4. **Si cambias models.py**: `python manage.py makemigrations && python manage.py migrate`
5. **Probar**: `python manage.py runserver 8080`

### Cambios seguros:
✅ Editar templates HTML (mantener UTF-8)
✅ Modificar views.py (lógica de negocio)
✅ Añadir campos a models.py (+ migración)
✅ Actualizar forms.py
✅ Cambiar estilos en base.html

### NO hacer:
❌ Tocar db.sqlite3 directamente
❌ Modificar migraciones existentes
❌ Cambiar codificación de archivos (mantener UTF-8)
❌ Eliminar símbolos € de templates (ya corregidos)

## 🔍 Búsqueda de Información

Si necesitas entender algo del proyecto:

1. **Documentación completa**: Lee `CONTEXTO_PROYECTO.md`
2. **Modelos de datos**: Lee `students/models.py` (tiene docstring detallado)
3. **Lógica de vistas**: Lee `students/views.py` (tiene docstring detallado)
4. **Estructura HTML**: Lee `students/templates/students/base.html`
5. **Rutas**: Lee `students/urls.py` y `autoescuela/urls.py`

## 🐛 Debugging

Si el usuario reporta un error:

1. **Leer el traceback completo** - especialmente el archivo y línea
2. **Verificar si es relacionado con codificación** - los templates ya están corregidos
3. **Comprobar si es un nuevo cambio** - preguntar qué modificó el usuario
4. **Leer el archivo problemático** - entender el contexto
5. **Proponer solución** - explicar el problema y la corrección

## 💡 Tips para Eficiencia

- **Para cambios en UI**: Leer template → Editar → Probar
- **Para cambios en lógica**: Leer views.py → Editar → Probar
- **Para nuevos campos**: Editar models.py → Editar forms.py → Editar template → Migrar
- **Siempre** usa `Edit` tool para archivos existentes, NO `Write`
- **Siempre** lee el archivo antes de editarlo

## 📚 Archivos de Documentación

1. **LEEME_CLAUDE.md** (este archivo) - Guía rápida para Claude
2. **CONTEXTO_PROYECTO.md** - Contexto completo e historial
3. **README.md** - Documentación técnica para usuarios
4. **LEEME_PRIMERO.txt** - Guía rápida en español
5. **RESUMEN_PROYECTO.txt** - Resumen del proyecto
6. **INSTRUCCIONES.txt** - Instrucciones de uso

## ✅ Checklist Antes de Empezar

Cuando el usuario te pida algo, verifica:

- [ ] ¿Entiendo qué es el proyecto? (Sistema gestión autoescuela)
- [ ] ¿Sé qué archivos modificar? (Lee esta guía)
- [ ] ¿Es un cambio en UI? → Templates
- [ ] ¿Es un cambio en lógica? → Views o Models
- [ ] ¿Necesito leer código antes? → Sí, SIEMPRE lee antes de editar
- [ ] ¿Voy a crear archivo nuevo? → Pregunta si es necesario
- [ ] ¿Voy a cambiar codificación? → NO, mantener UTF-8

## 🎓 Conceptos Clave del Negocio

- **Bono**: Paquete de clases prácticas que el alumno compra (default 50€)
- **Pago**: Dinero que el alumno entrega (puede ser parcial)
- **Deuda**: Suma total de bonos comprados
- **Pagado**: Suma total de dinero recibido
- **Pendiente**: deuda - pagado (si positivo, el alumno debe dinero)

---

**Última actualización**: Noviembre 2025
**Estado**: Sistema funcional, UTF-8 corregido, listo para usar
**Próximos pasos**: El usuario decidirá si quiere nuevas funcionalidades
