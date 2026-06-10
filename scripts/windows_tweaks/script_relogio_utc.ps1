# Requer privilegios de administrador
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Este script precisa ser executado como Administrador!"
    exit
}

$RegistryPath = "HKLM:\SYSTEM\CurrentControlSet\Control\TimeZoneInformation"

Write-Host "Configurando o relogio de hardware para usar Hora Local (Padrao)..." -ForegroundColor Yellow

if (Test-Path $RegistryPath) {
    Remove-ItemProperty -Path $RegistryPath -Name "RealTimeIsUniversal" -Force -ErrorAction SilentlyContinue
}

Write-Host "Concluido! Relogio de hardware configurado para Hora Local com sucesso." -ForegroundColor Green
