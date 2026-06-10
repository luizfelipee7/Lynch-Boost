@echo off
:: Padrao Lynch Boost - Sem acentos
echo ========================================================
echo LYNCH FPS BOOST - MENU DE CONTEXTO MODERNO (WIN 11)
echo ========================================================
echo.
echo Removendo chave de registro para reativar o menu padrao do Windows 11...
reg.exe delete "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f >nul 2>&1


echo.
echo OK! O Menu de Contexto original do Windows 11 foi restaurado.
exit
