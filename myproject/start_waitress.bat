@echo off
echo Attempting to change directory to "c:\ReceptionIQ\python Backend\myproject" >> "%USERPROFILE%\Desktop\waitress_log.txt"
cd /d "c:\ReceptionIQ\python Backend\myproject"
echo Current directory: %cd% >> "%USERPROFILE%\Desktop\waitress_log.txt"

if exist cert.pem (
    echo cert.pem found >> "%USERPROFILE%\Desktop\waitress_log.txt"
) else (
    echo cert.pem not found >> "%USERPROFILE%\Desktop\waitress_log.txt"
)

if exist key.pem (
    echo key.pem found >> "%USERPROFILE%\Desktop\waitress_log.txt"
) else (
    echo key.pem not found >> "%USERPROFILE%\Desktop\waitress_log.txt"
)

if exist myproject\wsgi.py (
    echo wsgi.py found >> "%USERPROFILE%\Desktop\waitress_log.txt"
) else (
    echo wsgi.py not found >> "%USERPROFILE%\Desktop\waitress_log.txt"
)

echo Checking waitress-serve.exe path >> "%USERPROFILE%\Desktop\waitress_log.txt"
if exist "C:\Program Files\Python313\Scripts\waitress-serve.exe" (
    echo waitress-serve.exe found >> "%USERPROFILE%\Desktop\waitress_log.txt"
) else (
    echo waitress-serve.exe not found >> "%USERPROFILE%\Desktop\waitress_log.txt"
)

echo Starting Waitress server at %date% %time% >> "%USERPROFILE%\Desktop\waitress_log.txt"

"C:\Program Files\Python313\Scripts\waitress-serve.exe" --listen=0.0.0.0:8002 myproject.wsgi:application >> "%USERPROFILE%\Desktop\waitress_log.txt" 2>&1

pause
