param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("Ativar", "Reverter")]
    [string]$Acao
)

# Requer privilegios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador!"
    exit 1
}

if ($Acao -eq "Ativar") {
    Write-Host "Desativando Mitigacoes de Kernel e Seguranca para FPS Maximo..." -ForegroundColor Red
    
    # 1. Desativar Spectre & Meltdown (FeatureSettingsOverride)
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" -Name "FeatureSettings" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" -Name "FeatureSettingsOverride" -Value 3 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" -Name "FeatureSettingsOverrideMask" -Value 3 -Type DWord -Force -ErrorAction SilentlyContinue

    # 2. Desativar Virtualization-Based Security (VBS / Core Isolation)
    $DeviceGuardPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard"
    if (!(Test-Path $DeviceGuardPath)) { New-Item -Path $DeviceGuardPath -Force | Out-Null }
    Set-ItemProperty -Path $DeviceGuardPath -Name "EnableVirtualizationBasedSecurity" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $DeviceGuardPath -Name "HVCIMATRequired" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    # Chaves de Sistema Ativas para VBS
    $DeviceGuardSystemPath = "HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard"
    if (!(Test-Path $DeviceGuardSystemPath)) { New-Item -Path $DeviceGuardSystemPath -Force | Out-Null }
    Set-ItemProperty -Path $DeviceGuardSystemPath -Name "EnableVirtualizationBasedSecurity" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    # Chaves de Sistema Ativas para Integridade de Memória (HVCI)
    $HVCIPath = "HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity"
    if (!(Test-Path $HVCIPath)) { New-Item -Path $HVCIPath -Force | Out-Null }
    Set-ItemProperty -Path $HVCIPath -Name "Enabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue


    Write-Host "[OK] Mitigacoes de seguranca desativadas! Reinicie o PC para o FPS maximo entrar em vigor." -ForegroundColor Green
} else {
    Write-Host "Reativando Mitigacoes de Kernel e Seguranca Padrao do Windows..." -ForegroundColor Green

    # 1. Restaurar Spectre & Meltdown
    Remove-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" -Name "FeatureSettings" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" -Name "FeatureSettingsOverride" -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" -Name "FeatureSettingsOverrideMask" -ErrorAction SilentlyContinue

    # 2. Restaurar Virtualization-Based Security (VBS)
    $DeviceGuardPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard"
    if (Test-Path $DeviceGuardPath) {
        Remove-ItemProperty -Path $DeviceGuardPath -Name "EnableVirtualizationBasedSecurity" -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $DeviceGuardPath -Name "HVCIMATRequired" -ErrorAction SilentlyContinue
    }

    $DeviceGuardSystemPath = "HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard"
    if (Test-Path $DeviceGuardSystemPath) {
        Set-ItemProperty -Path $DeviceGuardSystemPath -Name "EnableVirtualizationBasedSecurity" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    $HVCIPath = "HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity"
    if (Test-Path $HVCIPath) {
        Set-ItemProperty -Path $HVCIPath -Name "Enabled" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    }


    Write-Host "[OK] Mitigacoes de seguranca reativadas para o padrao. Reinicie o PC." -ForegroundColor Green
}
