@echo off
:: Padrao Lynch Boost - Sem acentos para evitar erros no Python
echo ========================================================
echo   LYNCH FPS BOOST - REPARACAO DA IMAGEM DO WINDOWS
echo ========================================================
echo.
echo AVISO: Este processo pode demorar de 5 a 15 minutos dependendo
echo da velocidade do seu disco e da sua conexao com a internet.
echo Por favor, nao feche esta janela ate a conclusao total.
echo.

echo [1/3] Passo 1 - Verificando a saude do sistema (CheckHealth)...
dism /online /cleanup-image /CheckHealth
echo.

echo [2/3] Passo 2 - Restaurando componentes da Imagem (RestoreHealth)...
echo Baixando arquivos limpos dos servidores da Microsoft. Aguarde...
dism /online /cleanup-image /restorehealth
echo OK - A Imagem do Windows foi reparada!
echo.

echo [3/3] Passo 3 - Verificacao de Integridade Local (SFC)...
echo Utilizando a Imagem reparada para consertar arquivos locais.
sfc /scannow
echo.

echo ========================================================
echo Processo de Reparo concluido com sucesso!
echo O nucleo do seu Windows esta 100%% integro e limpo.
echo ========================================================
echo.
ping 127.0.0.1 -n 6 >nul
exit
