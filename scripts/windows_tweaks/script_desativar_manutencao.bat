@echo off
:: Padrao Lynch Boost - Sem acentos para evitar erros no Python
echo ========================================================
echo   LYNCH FPS BOOST - LIMPEZA DE MANUTENCAO EM SEGUNDO PLANO
echo ========================================================
echo.

echo [1/3] Desativando tarefas do CEIP (Coleta de Dados)...
schtasks /change /tn "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator" /disable >nul 2>&1
schtasks /change /tn "\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip" /disable >nul 2>&1
schtasks /change /tn "\Microsoft\Windows\Customer Experience Improvement Program\KernelCeipTask" /disable >nul 2>&1
schtasks /change /tn "\Microsoft\Windows\Customer Experience Improvement Program\BthSQM" /disable >nul 2>&1

echo [2/3] Desativando Manutencao Automatica e Diagnosticos...
schtasks /change /tn "\Microsoft\Windows\TaskScheduler\Maintenance Configurator" /disable >nul 2>&1
schtasks /change /tn "\Microsoft\Windows\TaskScheduler\Idle Maintenance" /disable >nul 2>&1
schtasks /change /tn "\Microsoft\Windows\TaskScheduler\Regular Maintenance" /disable >nul 2>&1
schtasks /change /tn "\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector" /disable >nul 2>&1
schtasks /change /tn "\Microsoft\Windows\Diagnosis\Scheduled" /disable >nul 2>&1

echo [3/4] Desativando verificacao de Mapas e Disco em background...
schtasks /change /tn "\Microsoft\Windows\Maps\MapsUpdateTask" /disable >nul 2>&1
schtasks /change /tn "\Microsoft\Windows\Maps\MapsToastTask" /disable >nul 2>&1
schtasks /change /tn "\Microsoft\Windows\Chkdsk\ProactiveScan" /disable >nul 2>&1

echo [4/4] Desativando a Manutencao Automatica no Registro...
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Maintenance" /v "MaintenanceDisabled" /t REG_DWORD /d "1" /f >nul 2>&1

echo OK - Todas as tarefas inuteis de manutencao foram aniquiladas!
echo.
ping 127.0.0.1 -n 4 >nul
exit
