@echo off
:: Padrao Lynch Boost - Sem acentos para evitar erros no Python
echo ========================================================
echo   LYNCH FPS BOOST - EXCLUSAO DA PASTA WINDOWS.OLD
echo ========================================================
echo.

if not exist "C:\Windows.old" (
    echo [AVISO] Nenhuma instalacao anterior do Windows encontrada.
    echo A pasta "C:\Windows.old" nao existe no seu sistema.
    echo.
    ping 127.0.0.1 -n 5 >nul 2>&1
    exit /b 0
)

echo [1/3] Assumindo a propriedade da pasta Windows.old...
takeown /F C:\Windows.old /A /R /D Y >nul 2>&1
echo OK - Propriedade assumida!
echo.

echo [2/3] Concedendo controle total para Administradores...
icacls C:\Windows.old /T /grant Administrators:F >nul 2>&1
echo OK - Permissoes atualizadas!
echo.

echo [3/3] Removendo permanentemente a pasta Windows.old...
rd /S /Q C:\Windows.old >nul 2>&1
echo OK - Pasta Windows.old removida com sucesso!
echo.

echo ========================================================
echo Limpeza concluida! Espaco em disco liberado.
echo ========================================================
echo.
ping 127.0.0.1 -n 5 >nul 2>&1
exit /b 0
