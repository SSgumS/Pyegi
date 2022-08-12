set LOGFILE=install.bat.log
call :LOG > %LOGFILE% 2>&1
exit /B

:LOG
powershell -ExecutionPolicy Bypass -File "./src/dependency/Pyegi/Installer/install.ps1"
