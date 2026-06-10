@echo off
:: Padrao Lynch Boost - Sem acentos
echo ========================================================
echo LYNCH FPS BOOST - MENU DE CONTEXTO CLASSICO (WIN 11)
echo ========================================================
echo.
echo Adicionando chave de registro para desativar o "Mostrar mais opcoes"...
reg.exe add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve >nul 2>&1


echo.
echo OK! O Menu de Contexto classico do Windows 10 foi restaurado.
exit
