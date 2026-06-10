@echo off
:: Padrao Lynch Boost - Sem acentos
echo ========================================================
echo   LYNCH FPS BOOST - LIMPEZA AVANCADA (SISTEMA)
echo ========================================================
echo.

echo [1/2] Limpando Temporarios do Sistema e Lixeira...
del /q /f /s "%temp%\*.*" >nul 2>&1
for /d %%x in ("%temp%\*") do rmdir /s /q "%%x" >nul 2>&1
del /q /f /s "%SystemRoot%\Temp\*.*" >nul 2>&1
for /d %%x in ("%SystemRoot%\Temp\*") do rmdir /s /q "%%x" >nul 2>&1
rd /s /q %systemdrive%\$Recycle.bin >nul 2>&1
echo OK - Arquivos de Cache Geral Limpos!
echo.

echo [2/2] Limpando Rastros e Lixo Profundo do Windows...
:: Limpeza de Logs, SoftwareDistribution (Update) e WebCache (Caches ocultos)
rmdir /s /q "C:\Windows\SoftwareDistribution\Download" >nul 2>&1
rmdir /s /q "C:\Windows\Panther" >nul 2>&1
rmdir /s /q "C:\Users\%USERNAME%\AppData\Local\Microsoft\Windows\INetCache" >nul 2>&1
del /q /f /s "C:\Users\%USERNAME%\AppData\Local\Microsoft\Windows\WebCache\*.log" >nul 2>&1
echo OK - Arquivos Inuteis de Atualizacao e Logs Excluidos!
echo.

echo ========================================================
echo Processo concluido com sucesso! O Windows esta mais leve.
echo ========================================================
ping 127.0.0.1 -n 5 >nul 2>&1
exit /b 0