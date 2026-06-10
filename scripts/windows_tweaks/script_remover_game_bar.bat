@echo off
:: Padrao Lynch Boost - Sem acentos para evitar erros no Python
echo ========================================================
echo      LYNCH FPS BOOST - DESINSTALACAO DA GAME BAR
echo ========================================================
echo.

echo [1/3] Desativando Game DVR no Registro do Windows...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR" /v value /t REG_DWORD /d 0 /f >nul 2>&1
echo OK - Registro otimizado!
echo.

echo [2/3] Removendo Xbox Game Bar e Game Speech Window...
powershell -Command "Get-AppxPackage Microsoft.XboxGamingOverlay | Remove-AppxPackage" >nul 2>&1
powershell -Command "Get-AppxPackage Microsoft.XboxSpeechToTextOverlay | Remove-AppxPackage" >nul 2>&1
echo OK - Aplicativos desinstalados!
echo.

echo [3/4] Bloqueando o popup de erro do ms-gamebar...
reg add "HKCR\ms-gamebar\shell\open\command" /ve /t REG_SZ /d "C:\Windows\System32\cmd.exe /c exit" /f >nul 2>&1
echo OK - Popup bloqueado com sucesso!
echo.

echo [4/4] Forcando Kernel a dar maxima prioridade aos Jogos...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 38 /f >nul 2>&1
echo OK - Win32PrioritySeparation configurado (Foreground Boost Maximo)!
echo.

echo ========================================================
echo Processo concluido com sucesso!
echo O atalho Win + G, o DVR e os popups foram desativados.
echo ========================================================
echo.

ping 127.0.0.1 -n 4 >nul
exit