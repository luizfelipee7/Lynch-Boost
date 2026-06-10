@echo off
:: Padrao Lynch Boost - Sem acentos para evitar erros no Python
echo ========================================================
echo   LYNCH FPS BOOST - LIMPEZA DE CACHE (APPS E BROWSERS)
echo ========================================================
echo.

echo [1/2] Fechando aplicativos e navegadores para liberar arquivos...
taskkill /f /im chrome.exe >nul 2>&1
taskkill /f /im msedge.exe >nul 2>&1
taskkill /f /im brave.exe >nul 2>&1
taskkill /f /im vivaldi.exe >nul 2>&1
taskkill /f /im firefox.exe >nul 2>&1
taskkill /f /im Spotify.exe >nul 2>&1
taskkill /f /im OneDrive.exe >nul 2>&1
taskkill /f /im TeamViewer.exe >nul 2>&1
taskkill /f /im TeamViewer_Service.exe >nul 2>&1
taskkill /f /im vmware.exe >nul 2>&1
echo OK - Processos finalizados!
echo.

echo [2/2] Limpando arquivos de cache temporarios...

:: --- SPOTIFY ---
echo Limpando cache do Spotify...
rmdir /q /s "%LocalAppData%\Spotify\Storage" >nul 2>&1
rmdir /q /s "%LocalAppData%\Spotify\Browser\Cache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Spotify\Data" >nul 2>&1

:: --- ONEDRIVE ---
echo Limpando caches e logs do OneDrive...
rmdir /q /s "%LocalAppData%\Microsoft\OneDrive\logs" >nul 2>&1
rmdir /q /s "%LocalAppData%\Microsoft\OneDrive\setup" >nul 2>&1

:: --- ADOBE ---
echo Limpando Media Cache do Adobe...
rmdir /q /s "%LocalAppData%\Adobe\Common\Media Cache Files" >nul 2>&1
rmdir /q /s "%AppData%\Adobe\Common\Media Cache Files" >nul 2>&1
rmdir /q /s "%LocalAppData%\Adobe\UXP\PluginsCache" >nul 2>&1
rmdir /q /s "%AppData%\Adobe\UXP\PluginsCache" >nul 2>&1

:: --- VMWARE ---
echo Limpando caches e logs do VMWare...
rmdir /q /s "%LocalAppData%\VMware" >nul 2>&1
rmdir /q /s "%AppData%\VMware" >nul 2>&1

:: --- TEAMVIEWER ---
echo Limpando logs e temporarios do TeamViewer...
rmdir /q /s "%LocalAppData%\TeamViewer" >nul 2>&1
rmdir /q /s "%AppData%\TeamViewer" >nul 2>&1

:: --- MICROSOFT EDGE ---
echo Limpando Microsoft Edge...
rmdir /q /s "%LocalAppData%\Microsoft\Edge\User Data\Default\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Microsoft\Edge\User Data\GrShaderCache\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Microsoft\Edge\User Data\ShaderCache\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Microsoft\Edge\User Data\Default\Cache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Microsoft\Edge\User Data\Default\Code Cache" >nul 2>&1

:: --- GOOGLE CHROME ---
echo Limpando Google Chrome...
rmdir /q /s "%LocalAppData%\Google\Chrome\User Data\Default\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Google\Chrome\User Data\GrShaderCache\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Google\Chrome\User Data\ShaderCache\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Google\Chrome\User Data\Default\Cache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Google\Chrome\User Data\Default\Code Cache" >nul 2>&1

:: --- BRAVE BROWSER ---
echo Limpando Brave Browser...
rmdir /q /s "%LocalAppData%\BraveSoftware\Brave-Browser\User Data\Default\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\BraveSoftware\Brave-Browser\User Data\GrShaderCache\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\BraveSoftware\Brave-Browser\User Data\ShaderCache\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\BraveSoftware\Brave-Browser\User Data\Default\Cache" >nul 2>&1
rmdir /q /s "%LocalAppData%\BraveSoftware\Brave-Browser\User Data\Default\Code Cache" >nul 2>&1

:: --- VIVALDI ---
echo Limpando Vivaldi...
rmdir /q /s "%LocalAppData%\Vivaldi\User Data\Default\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Vivaldi\User Data\GrShaderCache\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Vivaldi\User Data\ShaderCache\GPUCache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Vivaldi\User Data\Default\Cache" >nul 2>&1
rmdir /q /s "%LocalAppData%\Vivaldi\User Data\Default\Code Cache" >nul 2>&1

:: --- MOZILLA FIREFOX ---
echo Limpando Mozilla Firefox...
set "ff_parent=%LocalAppData%\Mozilla\Firefox\Profiles"
for /f "tokens=*" %%a in ('dir /b "%ff_parent%" 2^>nul ^| findstr ".*\.default*"') do (
    rmdir /q /s "%ff_parent%\%%a\shader-cache" >nul 2>&1
    rmdir /q /s "%ff_parent%\%%a\cache2" >nul 2>&1
    rmdir /q /s "%ff_parent%\%%a\jumpListCache" >nul 2>&1
    rmdir /q /s "%ff_parent%\%%a\startupCache" >nul 2>&1
)

echo.
echo OK - Caches de navegadores e aplicativos limpos com sucesso!
echo ========================================================
echo.
exit /b 0
