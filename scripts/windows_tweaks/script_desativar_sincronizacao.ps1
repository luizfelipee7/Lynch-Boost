param([string]$Acao = "Ativar")

$RegistryPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\SettingSync\Groups"
$Groups = @("Accessibility", "AppSync", "BrowserSettings", "Credentials", "DesktopTheme", "Language", "PackageState", "Personalization", "StartLayout", "Windows")
$PolicyPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\SettingSync"

if ($Acao -eq "Ativar") {
    Write-Host "Desativando a Sincronizacao de Configuracoes nas Nuvens..." -ForegroundColor Yellow
    
    # Desativar cada grupo de sincronizacao do usuario
    foreach ($Group in $Groups) {
        $GroupPath = "$RegistryPath\$Group"
        if (!(Test-Path $GroupPath)) {
            New-Item -Path $GroupPath -Force | Out-Null
        }
        Set-ItemProperty -Path $GroupPath -Name "Enabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    }
    
    # Desativar via Politica de Grupo (GPO)
    if (!(Test-Path $PolicyPath)) {
        New-Item -Path $PolicyPath -Force | Out-Null
    }
    Set-ItemProperty -Path $PolicyPath -Name "DisableSettingSync" -Value 2 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $PolicyPath -Name "DisableSettingSyncUserOverride" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue

    Write-Host "Concluido! A sincronizacao em segundo plano foi desativada." -ForegroundColor Green
} else {
    Write-Host "Reativando a Sincronizacao de Configuracoes nas Nuvens..." -ForegroundColor Yellow
    
    # Reativar cada grupo de sincronizacao do usuario
    foreach ($Group in $Groups) {
        $GroupPath = "$RegistryPath\$Group"
        if (!(Test-Path $GroupPath)) {
            New-Item -Path $GroupPath -Force | Out-Null
        }
        Set-ItemProperty -Path $GroupPath -Name "Enabled" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    }
    
    # Remover restricoes de GPO
    if (Test-Path $PolicyPath) {
        Remove-ItemProperty -Path $PolicyPath -Name "DisableSettingSync" -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $PolicyPath -Name "DisableSettingSyncUserOverride" -Force -ErrorAction SilentlyContinue
    }

    Write-Host "Concluido! A sincronizacao em segundo plano foi reativada." -ForegroundColor Green
}
