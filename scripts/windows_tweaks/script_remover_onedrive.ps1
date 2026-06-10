# ========================================================
# LYNCH FPS BOOST - REMOCAO DO MICROSOFT ONEDRIVE V4.0
# ========================================================

Write-Output "Matando processos do OneDrive e destrancando arquivos..."
taskkill.exe /F /IM "OneDrive.exe" 2>$null
taskkill.exe /F /IM "FileSyncHelper.exe" 2>$null
taskkill.exe /F /IM "FileCoAuth.exe" 2>$null
taskkill.exe /F /IM "explorer.exe" 2>$null

Write-Output "Localizando e executando o desinstalador do nucleo Win32..."
$uninstallPaths = @(
    "$env:programfiles\Microsoft OneDrive\OneDriveSetup.exe",
    "${env:ProgramFiles(x86)}\Microsoft OneDrive\OneDriveSetup.exe",
    "$env:systemroot\System32\OneDriveSetup.exe",
    "$env:systemroot\SysWOW64\OneDriveSetup.exe"
)

foreach ($path in $uninstallPaths) {
    if (Test-Path $path) {
        Write-Output "Desinstalador encontrado em: $path"
        & $path /uninstall
        Start-Sleep -Seconds 3
    }
}

Write-Output "Removendo pacote UWP (Fantasma de Aplicativos)..."
Get-AppxPackage *OneDriveSync* | Remove-AppxPackage > $null 2>&1

Write-Output "Limpando chaves de desinstalacao e RAIZ do Registro..."
# Limpa chaves de desinstalacao que prendem o app no menu
Remove-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\OneDriveSetup.exe" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\OneDrive" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\OneDriveSetup.exe" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\OneDriveSetup.exe" -Force -Recurse -ErrorAction SilentlyContinue

# ANQUILACAO DAS CHAVES RAIZ (Telemetria, Cache e Updates)
Remove-Item -Path "HKCU:\Software\Microsoft\OneDrive" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path "HKLM:\SOFTWARE\Microsoft\OneDrive" -Force -Recurse -ErrorAction SilentlyContinue

Write-Output "Removendo pastas residuais fisicas do sistema..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$env:programfiles\Microsoft OneDrive"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "${env:ProgramFiles(x86)}\Microsoft OneDrive"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$env:localappdata\Microsoft\OneDrive"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$env:programdata\Microsoft OneDrive"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$env:systemdrive\OneDriveTemp"

Write-Output "Aniquilando a pasta de sincronizacao pessoal (Modo Trator)..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "$env:userprofile\OneDrive"

Write-Output "Limpando Tarefas Agendadas fantasmas do OneDrive..."
Get-ScheduledTask -TaskPath "\" -ErrorAction SilentlyContinue | Where-Object {$_.TaskName -match "OneDrive"} | Unregister-ScheduledTask -Confirm:$false > $null 2>&1

Write-Output "Removendo Variaveis de Ambiente da memoria RAM..."
[Environment]::SetEnvironmentVariable("OneDrive", $null, "User")
[Environment]::SetEnvironmentVariable("OneDriveConsumer", $null, "User")

Write-Output "Removendo icone da barra lateral do explorador..."
New-PSDrive -PSProvider "Registry" -Root "HKEY_CLASSES_ROOT" -Name "HKCR" | Out-Null
if (Test-Path "HKCR:\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}") {
    Set-ItemProperty -Path "HKCR:\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" "System.IsPinnedToNameSpaceTree" 0
}
if (Test-Path "HKCR:\Wow6432Node\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}") {
    Set-ItemProperty -Path "HKCR:\Wow6432Node\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" "System.IsPinnedToNameSpaceTree" 0
}
Remove-PSDrive "HKCR"

Write-Output "Removendo atalho de inicializacao para novos usuarios..."
reg load "hku\Default" "C:\Users\Default\NTUSER.DAT" > $null 2>&1
reg delete "HKEY_USERS\Default\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "OneDriveSetup" /f > $null 2>&1
reg unload "hku\Default" > $null 2>&1

Write-Output "Bloqueando o motor do OneDrive via Politica de Grupo (Impedindo retornos)..."
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive" /v DisableFileSyncNGSC /t REG_DWORD /d 1 /f > $null 2>&1

Write-Output "Removendo entrada do menu iniciar..."
Remove-Item -Force -ErrorAction SilentlyContinue "$env:userprofile\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\OneDrive.lnk"

Write-Output "Reiniciando o explorador de arquivos..."
Start-Process "explorer.exe"

Write-Output "Processo concluido! O OneDrive e todo o seu lixo de registro foram obliterados."
Start-Sleep 5