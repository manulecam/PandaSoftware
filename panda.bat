@echo off
REM Cambia al directorio donde se encuentra este script
cd /d "D:\PROGRAMAS\PANDA"

REM Ejecuta el script de Python.
REM Asegúrate de que 'python' esté en tu PATH o usa la ruta completa a python.exe
python panda.py

REM Pausa la ventana de CMD para que no se cierre inmediatamente después de terminar
REM para que puedas ver los mensajes del log.
pause