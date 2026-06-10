# ========================================================
# LYNCH FPS BOOST - DESATIVAR TIMER COALESCING & GPU ENERGY
# ========================================================
# Este script otimiza a latência da CPU e da GPU desativando
# temporizadores de energia ociosa do kernel e drivers de
# telemetria de energia física em segundo plano.
# ========================================================

param (
    [ValidateSet("Ativar", "Reverter")]
    [string]$Acao = "Ativar"
)

# Requer privilégios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador!"
    exit 1
}

$RegistrySessionManager = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager"
$RegistrySessionManagerPower = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power"
$RegistrySessionManagerMemory = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
$RegistrySessionManagerKernel = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\kernel"
$RegistrySessionManagerExecutive = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Executive"
$RegistryPowerModernSleep = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\ModernSleep"
$RegistryPower = "HKLM:\SYSTEM\CurrentControlSet\Control\Power"
$RegistryGpuEnergyDrv = "HKLM:\SYSTEM\CurrentControlSet\Services\GpuEnergyDrv"
$RegistryGpuEnergyDr = "HKLM:\SYSTEM\CurrentControlSet\Services\GpuEnergyDr"
$RegistryTaggedEnergy = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\EnergyEstimation\TaggedEnergy"

if ($Acao -eq "Ativar") {
    Write-Host "Ativando Otimizacao de Timer Coalescing e Energia..." -ForegroundColor Cyan

    # 1. Desativar Timer Coalescing (Força a CPU a responder instantaneamente sem agrupar timers)
    Write-Host "[1/4] Desativando Timer Coalescing nos modulos do Kernel..." -ForegroundColor Yellow
    
    $SMPaths = @($RegistrySessionManager, $RegistrySessionManagerPower, $RegistrySessionManagerMemory, 
                 $RegistrySessionManagerKernel, $RegistrySessionManagerExecutive, $RegistryPowerModernSleep, $RegistryPower)
    
    foreach ($path in $SMPaths) {
        if (!(Test-Path $path)) { New-Item -Path $path -Force | Out-Null }
        Set-ItemProperty -Path $path -Name "CoalescingTimerInterval" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    # 2. Desativar Telemetria de Modern Sleep e Estimativa de Energia
    Write-Host "[2/4] Desativando telemetria de energia e Modern Standby..." -ForegroundColor Yellow
    if (!(Test-Path $RegistryPower)) { New-Item -Path $RegistryPower -Force | Out-Null }
    Set-ItemProperty -Path $RegistryPower -Name "PlatformAoAcOverride" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $RegistryPower -Name "EnergyEstimationEnabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $RegistryPower -Name "EventProcessorEnabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $RegistryPower -Name "CsEnabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    # 3. Desativar GPU Energy Driver (Reduz telemetria e polling da placa de vídeo)
    Write-Host "[3/4] Desativando drivers de telemetria de energia da GPU..." -ForegroundColor Yellow
    if (Test-Path $RegistryGpuEnergyDrv) {
        Set-ItemProperty -Path $RegistryGpuEnergyDrv -Name "Start" -Value 4 -Type DWord -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $RegistryGpuEnergyDr) {
        Set-ItemProperty -Path $RegistryGpuEnergyDr -Name "Start" -Value 4 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    # 4. Desativar Logs de TaggedEnergy
    Write-Host "[4/4] Bloqueando logs de telemetria TaggedEnergy em segundo plano..." -ForegroundColor Yellow
    if (!(Test-Path $RegistryTaggedEnergy)) { New-Item -Path $RegistryTaggedEnergy -Force | Out-Null }
    Set-ItemProperty -Path $RegistryTaggedEnergy -Name "DisableTaggedEnergyLogging" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $RegistryTaggedEnergy -Name "TelemetryMaxApplication" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $RegistryTaggedEnergy -Name "TelemetryMaxTagPerApplication" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    Write-Host "`n[OK] Otimizacoes de Timer Coalescing e Energia aplicadas com sucesso!" -ForegroundColor Green

} elseif ($Acao -eq "Reverter") {
    Write-Host "Revertendo Otimizacoes de Timer Coalescing e Energia..." -ForegroundColor Cyan

    # 1. Remover CoalescingTimerInterval
    Write-Host "[1/4] Restaurando agrupamento de timers do Kernel..." -ForegroundColor Yellow
    $SMPaths = @($RegistrySessionManager, $RegistrySessionManagerPower, $RegistrySessionManagerMemory, 
                 $RegistrySessionManagerKernel, $RegistrySessionManagerExecutive, $RegistryPowerModernSleep, $RegistryPower)
    
    foreach ($path in $SMPaths) {
        if (Test-Path $path) {
            Remove-ItemProperty -Path $path -Name "CoalescingTimerInterval" -ErrorAction SilentlyContinue
        }
    }

    # 2. Restaurar Modern Sleep e Estimativa de Energia
    Write-Host "[2/4] Reativando telemetria de energia e Modern Standby..." -ForegroundColor Yellow
    if (Test-Path $RegistryPower) {
        Remove-ItemProperty -Path $RegistryPower -Name "PlatformAoAcOverride" -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $RegistryPower -Name "EnergyEstimationEnabled" -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $RegistryPower -Name "EventProcessorEnabled" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $RegistryPower -Name "CsEnabled" -ErrorAction SilentlyContinue
    }

    # 3. Reativar GPU Energy Driver para o padrao (Manual / Demand)
    Write-Host "[3/4] Restaurando drivers de telemetria de energia da GPU..." -ForegroundColor Yellow
    if (Test-Path $RegistryGpuEnergyDrv) {
        Set-ItemProperty -Path $RegistryGpuEnergyDrv -Name "Start" -Value 3 -Type DWord -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $RegistryGpuEnergyDr) {
        Set-ItemProperty -Path $RegistryGpuEnergyDr -Name "Start" -Value 3 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    # 4. Remover TaggedEnergy keys
    Write-Host "[4/4] Desbloqueando logs de telemetria TaggedEnergy..." -ForegroundColor Yellow
    if (Test-Path $RegistryTaggedEnergy) {
        Remove-ItemProperty -Path $RegistryTaggedEnergy -Name "DisableTaggedEnergyLogging" -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $RegistryTaggedEnergy -Name "TelemetryMaxApplication" -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $RegistryTaggedEnergy -Name "TelemetryMaxTagPerApplication" -ErrorAction SilentlyContinue
    }

    Write-Host "`n[OK] Otimizacoes de Timer Coalescing e Energia revertidas para o padrao com sucesso!" -ForegroundColor Green
}
