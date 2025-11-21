#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Crear tipos de carnet por defecto si no existen
python manage.py createdefaultlicenses

# Generar tokens para pagos que no tienen
python manage.py generate_payment_tokens

# Crear superusuario por defecto si no existe
python manage.py createdefaultsu
