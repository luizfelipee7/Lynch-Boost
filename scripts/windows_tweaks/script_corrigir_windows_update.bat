@echo off
:: Padrao Lynch Boost - Sem acentos para evitar erros no Python
echo ========================================================
echo   LYNCH FPS BOOST - REPARACAO DO WINDOWS UPDATE
echo ========================================================
echo.

echo [1/4] Finalizando servicos de atualizacao de segundo plano...
net stop wuauserv >nul 2>&1
net stop cryptSvc >nul 2>&1
net stop bits >nul 2>&1
net stop msiserver >nul 2>&1
echo OK - Servicos finalizados!
echo.

echo [2/4] Limpando arquivos de fila e logs acumulados...
del /f /q /s "%ALLUSERSPROFILE%\Application Data\Microsoft\Network\Downloader\qmgr*.dat" >nul 2>&1
echo OK - Fila de transferencia limpa!
echo.

echo [3/4] Excluindo pastas de cache corrompidas...
rmdir /s /q "C:\Windows\SoftwareDistribution" >nul 2>&1
rmdir /s /q "C:\Windows\System32\catroot2" >nul 2>&1
echo OK - Pastas de cache de atualizacao removidas!
echo.

echo [4/4] Reiniciando os servicos limpos do zero...
net start wuauserv >nul 2>&1
net start cryptSvc >nul 2>&1
net start bits >nul 2>&1
net start msiserver >nul 2>&1
echo OK - Servicos de atualizacao iniciados!
echo.

echo Iniciando busca imediata por novas atualizacoes (Scan)...
usoclient StartScan >nul 2>&1
echo.

echo ========================================================
echo Reparo do Windows Update concluido com sucesso!
echo O cache foi limpo e o servico reiniciado.
echo ========================================================
echo.
ping 127.0.0.1 -n 6 >nul 2>&1
exit /b 0
