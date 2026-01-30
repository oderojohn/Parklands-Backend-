@echo off
cd /d "C:\app\python Backend\myproject"

echo Starting Waitress server at %date% %time% >> logs.txt
echo Starting Waitress server at %date% %time% >> "%USERPROFILE%\Desktop\waitress_log.txt"

"C:\Program Files\Python313\python.exe" -m waitress.serve --listen=0.0.0.0:8000 myproject.wsgi:application >> logs.txt 2>&1
"C:\Program Files\Python313\python.exe" -m waitress.serve --listen=0.0.0.0:8000 myproject.wsgi:application >> "%USERPROFILE%\Desktop\waitress_log.txt" 2>&1

pause
