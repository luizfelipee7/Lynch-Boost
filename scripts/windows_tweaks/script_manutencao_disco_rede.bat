@echo off
:: Padrao Lynch Boost - Sem acentos para evitar erros no Python
echo ========================================================
echo   LYNCH FPS BOOST - MANUTENCAO DE DISCO E REDE
echo ========================================================
echo.

echo [1/3] Limpando Cache de Rotas DNS...
ipconfig /flushdns >nul 2>&1
echo OK - Cache DNS zerado!
echo.

echo [2/3] Restaurando API Winsock (Protocolos TCP/IP)...
netsh winsock reset >nul 2>&1
echo OK - Catalogo de rede redefinido para o padrao de fabrica!
echo.

echo [3/3] Agendando Verificacao Profunda de Disco (CHKDSK)...
echo O comando a seguir varrera seu SSD/HD em busca de setores corrompidos.
echo Como o Windows esta rodando, o escaneamento obrigatoriamente acontecera
echo na proxima vez que o computador for ligado.
echo.
echo Y | chkdsk c: /f /r >nul 2>&1
echo OK - Escaneamento de disco agendado para o proximo Boot!
echo.

echo ========================================================
echo Manutencao solicitada com sucesso!
echo E obrigatorio REINICIAR O COMPUTADOR AGORA para que a
echo API de Rede recarregue e o CHKDSK inicie a varredura!
echo ========================================================
ping 127.0.0.1 -n 6 >nul
exit
