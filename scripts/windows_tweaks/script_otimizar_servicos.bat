@echo off
:: Padrao Lynch Boost - Sem acentos para evitar erros no Python
echo ========================================================
echo   LYNCH FPS BOOST - OTIMIZACAO DE SERVICOS DO WINDOWS
echo ========================================================
echo.

echo Parando e desativando servicos vampiros que rodam em segundo plano...
echo Mantendo intactos: Windows Update, Defender, Bluetooth, Xbox e Impressora.
echo.

:: 1. Telemetria e Diagnosticos
echo [1/5] Desativando Telemetria e Relatorios de Erro...
sc config "DiagTrack" start= disabled >nul 2>&1
sc stop "DiagTrack" >nul 2>&1
sc config "WerSvc" start= disabled >nul 2>&1
sc stop "WerSvc" >nul 2>&1
sc config "dmwappushservice" start= disabled >nul 2>&1
sc stop "dmwappushservice" >nul 2>&1

:: 2. Hosts de Politica de Diagnostico
echo [2/5] Desativando Servicos de Diagnostico Continuo...
sc config "DPS" start= disabled >nul 2>&1
sc stop "DPS" >nul 2>&1
sc config "WdiServiceHost" start= disabled >nul 2>&1
sc stop "WdiServiceHost" >nul 2>&1
sc config "WdiSystemHost" start= disabled >nul 2>&1
sc stop "WdiSystemHost" >nul 2>&1

:: 3. Sensores, Mapas e Localizacao
echo [3/5] Removendo suporte inutil para Mapas Offline (Preservando GPS e Localizacao)...
sc config "MapsBroker" start= disabled >nul 2>&1
sc stop "MapsBroker" >nul 2>&1
sc config "lfsvc" start= demand >nul 2>&1
sc config "SensorDataService" start= demand >nul 2>&1
sc config "SensrSvc" start= demand >nul 2>&1

:: 4. Rastreamento e Registro Remoto (Seguranca e I/O)
echo [4/5] Bloqueando Registro Remoto e Rastreamento de Links Distribuido...
sc config "RemoteRegistry" start= disabled >nul 2>&1
sc stop "RemoteRegistry" >nul 2>&1
sc config "TrkWks" start= disabled >nul 2>&1
sc stop "TrkWks" >nul 2>&1

:: 5. Bloatware de Loja, Empresa e Familia
echo [5/5] Desativando Modo Varejo, Apps Empresariais e Controle dos Pais...
sc config "RetailDemo" start= disabled >nul 2>&1
sc stop "RetailDemo" >nul 2>&1
sc config "EntAppSvc" start= disabled >nul 2>&1
sc stop "EntAppSvc" >nul 2>&1
sc config "WpcSvc" start= disabled >nul 2>&1
sc stop "WpcSvc" >nul 2>&1
sc config "SysMain" start= disabled >nul 2>&1
sc stop "SysMain" >nul 2>&1

echo.
echo OK - A limpa de servicos foi concluida com sucesso!
echo.
ping 127.0.0.1 -n 4 >nul
exit
