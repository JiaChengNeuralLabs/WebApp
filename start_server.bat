@echo off
echo ========================================
echo Autoescuela Carrasco - Sistema de Gestion
echo ========================================
echo.
cd /d %~dp0
call venv\Scripts\activate.bat
echo Iniciando servidor...
echo.
echo Usuario: admin
echo Contrasena: admin123
echo.
echo Abriendo navegador en http://localhost:8080
echo.
echo Presiona Ctrl+C para detener el servidor
echo.
timeout /t 2 >nul
start http://localhost:8080/students/login/
python manage.py runserver 8080
