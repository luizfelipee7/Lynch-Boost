@echo off
:: Padrao Lynch Boost - Sem acentos para evitar erros no Python
echo ========================================================
echo      LYNCH FPS BOOST - DESATIVAR HIBERNACAO
echo ========================================================
echo.

echo Desligando o arquivo hiberfil.sys no sistema...
powercfg.exe /hibernate off

echo.
echo OK - Hibernacao desativada com sucesso! Espaco no SSD liberado.
echo ========================================================
echo.

exit /b 0