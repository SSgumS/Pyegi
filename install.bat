@echo off

powershell -Command " Start-Process PowerShell -Verb RunAs \""-Command `\""cd '%cd%'; powershell -NoExit -ExecutionPolicy Bypass -File './src/dependency/Pyegi/Installer/install.ps1' %~1;`\""\"" "
exit /b
