# Guía de Despliegue en Render.com

## Preparación del Proyecto

El proyecto ya está preparado para desplegar en Render.com con las siguientes configuraciones:

### Archivos Necesarios ✅
- `requirements.txt` - Dependencias de Python
- `build.sh` - Script de construcción para Render
- `autoescuela/settings.py` - Configurado para producción

### Dependencias Instaladas
- **Django 5.2.8** - Framework web
- **gunicorn** - Servidor WSGI para producción
- **whitenoise** - Para servir archivos estáticos
- **psycopg2-binary** - Driver de PostgreSQL
- **dj-database-url** - Configuración de base de datos desde URL

## Pasos para Desplegar en Render.com

### 1. Crear Cuenta en Render.com
1. Ve a https://render.com
2. Regístrate con GitHub (recomendado)

### 2. Crear una Base de Datos PostgreSQL
1. En el dashboard de Render, haz clic en "New +" → "PostgreSQL"
2. Configuración:
   - **Name**: `autoescuela-db` (o el nombre que prefieras)
   - **Database**: `autoescuela`
   - **User**: Se genera automáticamente
   - **Region**: Elige la más cercana (Frankfurt para Europa)
   - **Plan**: Free (para empezar)
3. Haz clic en "Create Database"
4. **IMPORTANTE**: Copia la "Internal Database URL" que aparece en la página

### 3. Crear el Web Service
1. En el dashboard, haz clic en "New +" → "Web Service"
2. Conecta tu repositorio de GitHub: `JiaChengNeuralLabs/WebApp`
3. Configuración:
   - **Name**: `autoescuela-carrasco`
   - **Region**: La misma que elegiste para la base de datos
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn autoescuela.wsgi:application`
   - **Plan**: Free (para empezar)

### 4. Configurar Variables de Entorno
En la sección "Environment Variables", añade las siguientes:

```
SECRET_KEY=tu-clave-secreta-aqui-genera-una-nueva
DEBUG=False
ALLOWED_HOSTS=tu-dominio-render.onrender.com
DATABASE_URL=la-url-interna-de-postgresql-que-copiaste
```

**Para generar una SECRET_KEY segura**, puedes usar:
```python
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

**Ejemplo de ALLOWED_HOSTS**:
```
autoescuela-carrasco.onrender.com,autoescuela-carrasco-abc123.onrender.com
```

### 5. Desplegar
1. Haz clic en "Create Web Service"
2. Render automáticamente:
   - Clonará tu repositorio
   - Ejecutará `build.sh` (instala dependencias, collectstatic, migrate)
   - Iniciará el servidor con gunicorn

### 6. Crear Superusuario en Producción
Una vez desplegado:
1. Ve a tu web service en Render
2. Haz clic en "Shell" en el menú lateral
3. Ejecuta:
```bash
python manage.py createsuperuser
```
4. Sigue las instrucciones para crear el usuario admin

## Verificar el Despliegue

1. Visita tu URL: `https://tu-servicio.onrender.com/students/login/`
2. Inicia sesión con las credenciales que creaste
3. Verifica que todo funcione correctamente

## Mantenimiento

### Actualizar el Código
1. Haz cambios en tu código local
2. Commit y push a GitHub:
```bash
git add .
git commit -m "Descripción del cambio"
git push
```
3. Render detectará automáticamente el push y redesplegar

### Ver Logs
- En el dashboard de Render, ve a tu web service
- Haz clic en "Logs" para ver los logs en tiempo real

### Ejecutar Migraciones Manualmente
Si necesitas ejecutar migraciones después de un cambio en modelos:
1. Ve a "Shell" en Render
2. Ejecuta: `python manage.py migrate`

## Troubleshooting

### Error 500 - Internal Server Error
- Revisa los logs en Render
- Verifica que todas las variables de entorno estén correctas
- Asegúrate de que ALLOWED_HOSTS incluye tu dominio

### Static Files no se cargan
- Verifica que `build.sh` ejecutó correctamente
- Ejecuta manualmente en Shell: `python manage.py collectstatic --no-input`

### Base de datos vacía
- Ejecuta las migraciones en Shell: `python manage.py migrate`
- Crea el superusuario: `python manage.py createsuperuser`

## Costos

### Plan Free de Render
- ✅ Web Service: Gratis (con limitaciones)
  - Se "duerme" después de 15 minutos de inactividad
  - Tarda ~30 segundos en despertar
  - 750 horas/mes de uso
- ✅ PostgreSQL: Gratis
  - 1GB de almacenamiento
  - Suficiente para empezar

### Plan Starter ($7/mes por servicio)
- Sin "sleep"
- Mejor rendimiento
- Recomendado para uso en producción real

## Seguridad en Producción

✅ **Configurado**:
- DEBUG=False en producción
- SECRET_KEY desde variable de entorno
- HTTPS forzado (SSL redirect)
- Cookies seguras
- XSS protection
- Content type sniffing protection

## Notas Importantes

1. **Base de Datos**: El plan free de PostgreSQL se elimina después de 90 días de inactividad
2. **Backups**: Render no hace backups automáticos en el plan free. Considera exportar datos regularmente
3. **Dominio Personalizado**: Puedes configurar tu propio dominio en Settings → Custom Domain

## Contacto y Soporte

- **Documentación Render**: https://render.com/docs
- **Soporte Render**: https://community.render.com
- **Documentación Django**: https://docs.djangoproject.com/en/5.2/howto/deployment/
