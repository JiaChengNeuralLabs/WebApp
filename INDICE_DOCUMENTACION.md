# 📚 Índice de Documentación - Autoescuela Carrasco

## 🤖 Para Claude Code (Lee PRIMERO)

### 1️⃣ LEEME_CLAUDE.md ⭐ **EMPEZAR AQUÍ**
**Propósito**: Guía rápida para Claude Code con todo el contexto necesario
**Contenido**:
- Contexto del proyecto en 2 minutos
- Credenciales de acceso
- Archivos más importantes
- Historia del problema de codificación UTF-8 (RESUELTO)
- Checklist antes de empezar
- Tips de eficiencia

### 2️⃣ CONTEXTO_PROYECTO.md
**Propósito**: Documentación técnica completa del proyecto
**Contenido**:
- Información general y propósito
- Arquitectura técnica detallada
- Descripción de modelos, vistas, templates
- Historial de problemas resueltos
- Cálculos financieros
- Comandos útiles
- Rutas del sistema
- Notas importantes para desarrollo

### 3️⃣ CHANGELOG.md
**Propósito**: Historial de cambios del proyecto
**Contenido**:
- Versión 1.0.1: Corrección UTF-8 + documentación
- Versión 1.0.0: Sistema inicial

---

## 👤 Para el Usuario (Jia Cheng)

### 4️⃣ README.md
**Propósito**: Documentación principal para usuarios y desarrolladores
**Contenido**:
- Características del sistema
- Instalación y uso
- Credenciales de acceso
- Guía de uso de la aplicación
- Estructura del proyecto detallada
- Información técnica (modelos, rutas, configuración)
- Solución de problemas

### 5️⃣ LEEME_PRIMERO.txt
**Propósito**: Guía de inicio rápido en español
**Contenido**:
- Instrucciones para iniciar el servidor
- Credenciales
- Primeros pasos

### 6️⃣ INSTRUCCIONES.txt
**Propósito**: Instrucciones de uso de la aplicación
**Contenido**:
- Cómo usar cada funcionalidad
- Flujo de trabajo típico

### 7️⃣ RESUMEN_PROYECTO.txt
**Propósito**: Resumen ejecutivo del proyecto
**Contenido**:
- Visión general
- Funcionalidades principales

### 8️⃣ GUIA_VISUAL.txt
**Propósito**: Guía visual de la interfaz
**Contenido**:
- Descripción de cada pantalla
- Elementos de la UI

### 9️⃣ COMANDOS_UTILES.txt
**Propósito**: Comandos Django útiles
**Contenido**:
- Comandos de gestión
- Comandos de base de datos
- Comandos de desarrollo

### 🔟 MEJORAS_FUTURAS.txt
**Propósito**: Ideas para futuras mejoras
**Contenido**:
- Lista de posibles características nuevas
- Mejoras sugeridas

---

## 📋 Guía de Lectura Recomendada

### Si eres Claude Code en una nueva sesión:
```
1. LEEME_CLAUDE.md (OBLIGATORIO - 3 min)
2. CONTEXTO_PROYECTO.md (si necesitas más detalles - 5 min)
3. Archivos de código según necesidad (models.py, views.py, etc.)
```

### Si eres un nuevo desarrollador:
```
1. README.md (documentación completa)
2. LEEME_PRIMERO.txt (inicio rápido)
3. CONTEXTO_PROYECTO.md (arquitectura)
4. Código fuente (students/models.py, students/views.py)
```

### Si eres el usuario (Jia Cheng):
```
1. LEEME_PRIMERO.txt (para empezar a usar)
2. INSTRUCCIONES.txt (para aprender a usar cada función)
3. README.md (si tienes problemas técnicos)
```

### Si buscas información específica:
- **¿Cómo funciona la base de datos?** → CONTEXTO_PROYECTO.md (sección "Modelos de Base de Datos")
- **¿Cómo usar la aplicación?** → INSTRUCCIONES.txt
- **¿Qué comandos ejecutar?** → COMANDOS_UTILES.txt
- **¿Qué cambió recientemente?** → CHANGELOG.md
- **¿Problemas técnicos?** → README.md (sección "Solución de Problemas")
- **¿Arquitectura del código?** → CONTEXTO_PROYECTO.md + README.md

---

## 🗂️ Estructura de Archivos del Proyecto

```
WebApp/
│
├── 📚 DOCUMENTACIÓN (10 archivos)
│   ├── LEEME_CLAUDE.md ⭐        # Para Claude Code (LEER PRIMERO)
│   ├── CONTEXTO_PROYECTO.md     # Documentación técnica completa
│   ├── CHANGELOG.md             # Historial de cambios
│   ├── README.md                # Documentación principal
│   ├── LEEME_PRIMERO.txt        # Inicio rápido
│   ├── INSTRUCCIONES.txt        # Guía de uso
│   ├── RESUMEN_PROYECTO.txt     # Resumen ejecutivo
│   ├── GUIA_VISUAL.txt          # Guía de interfaz
│   ├── COMANDOS_UTILES.txt      # Comandos Django
│   └── MEJORAS_FUTURAS.txt      # Ideas futuras
│
├── ⚙️ CONFIGURACIÓN DJANGO
│   ├── autoescuela/             # Proyecto Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── manage.py
│
├── 🎓 APLICACIÓN PRINCIPAL
│   └── students/                # App de gestión de alumnos
│       ├── models.py            # 4 modelos (con docstring)
│       ├── views.py             # 9 vistas (con docstring)
│       ├── forms.py             # 3 formularios
│       ├── urls.py              # Rutas
│       ├── admin.py             # Admin Django
│       ├── migrations/          # Migraciones DB
│       └── templates/students/  # 8 templates HTML
│           ├── base.html        # Base (con comentario)
│           ├── student_detail.html  # Con € corregidos
│           ├── payment_form.html    # Con € corregidos
│           ├── voucher_form.html    # Con € corregidos
│           └── ...
│
├── 🗄️ BASE DE DATOS
│   └── db.sqlite3               # SQLite database
│
├── 🐍 ENTORNO PYTHON
│   └── venv/                    # Virtual environment
│
└── 🚀 SCRIPTS
    └── start_server.bat         # Iniciar servidor (doble clic)
```

---

## 💡 Tips Rápidos

### Para Claude Code:
- **Siempre** lee `LEEME_CLAUDE.md` al empezar una nueva sesión
- **Antes de modificar código**, lee el archivo primero con Read tool
- **Los símbolos € están corregidos** - no los toques
- **Usa Edit** para archivos existentes, no Write

### Para Desarrolladores:
- Todos los archivos HTML están en UTF-8 sin BOM
- Los docstrings están en español
- Bootstrap 5.3 + Bootstrap Icons 1.11.0
- Django 5.2.8 + Python 3.13

### Para Usuarios:
- Usuario: admin / Contraseña: admin123
- Doble clic en `start_server.bat` para iniciar
- Acceder a http://localhost:8080/students/login/

---

**Actualizado**: Noviembre 2025
**Versión del sistema**: 1.0.1
