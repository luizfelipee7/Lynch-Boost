# ========================================================
# LYNCH FPS BOOST - OTIMIZADOR DE ENERGIA E CPU AMD
# ========================================================
# Este script otimiza temporizadores do kernel, latencia de
# energia e transicoes de clock especificamente para processadores AMD Ryzen.
# ========================================================

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("Ativar", "Reverter")]
    [string]$Acao
)

# Requer privilégios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador!"
    exit 1
}

$RegistryKernel = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\kernel"
$RegistryPower = "HKLM:\SYSTEM\CurrentControlSet\Control\Power"
$RegistryCoreParkingSettings = "HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\0cc5b647-c1df-4637-891a-dec35c318583"

if ($Acao -eq "Ativar") {
    Write-Host "Ativando Ajustes Finos de Energia e CPU AMD..." -ForegroundColor Cyan

    # 1. DistributeTimers (Distribui timers de kernel entre os nucleos para aliviar o Core 0)
    Write-Host "[1/4] Aplicando DistributeTimers para distribuir carga de interrupcoes..." -ForegroundColor Yellow
    if (Test-Path $RegistryKernel) {
        Set-ItemProperty -Path $RegistryKernel -Name "DistributeTimers" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    # 2. EventProcessorEnabled (Reduz latencia de escalonador do processador)
    Write-Host "[2/4] Desativando processador de eventos de energia em segundo plano..." -ForegroundColor Yellow
    if (Test-Path $RegistryPower) {
        Set-ItemProperty -Path $RegistryPower -Name "EventProcessorEnabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    # 3. Powercfg Settings (Throttling e IdleScaling no plano ativo)
    Write-Host "[3/4] Desativando Throttling por software e otimizando transicoes de P-States..." -ForegroundColor Yellow
    powercfg -setacvalueindex scheme_current sub_processor THROTTLING 0 2>$null
    powercfg -setacvalueindex scheme_current sub_processor IDLESCALING 1 2>$null
    powercfg /setactive SCHEME_CURRENT 2>$null

    # 4. Desbloquear Minimo de Parking de Nucleos no Registro
    Write-Host "[4/4] Desbloqueando chaves de controle avançado de Core Parking..." -ForegroundColor Yellow
    if (Test-Path $RegistryCoreParkingSettings) {
        Set-ItemProperty -Path $RegistryCoreParkingSettings -Name "ValueMin" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    Write-Host "`n[OK] Ajustes de CPU AMD aplicados com sucesso! Reinicie o PC para o efeito completo do Kernel." -ForegroundColor Green

} elseif ($Acao -eq "Reverter") {
    Write-Host "Revertendo Ajustes de Energia e CPU AMD para o Padrao do Windows..." -ForegroundColor Cyan

    # 1. Restaurar DistributeTimers para o padrao (0)
    Write-Host "[1/4] Restaurando DistributeTimers para o padrao..." -ForegroundColor Yellow
    if (Test-Path $RegistryKernel) {
        Set-ItemProperty -Path $RegistryKernel -Name "DistributeTimers" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    # 2. Restaurar EventProcessorEnabled para o padrao (1)
    Write-Host "[2/4] Restaurando EventProcessorEnabled para o padrao..." -ForegroundColor Yellow
    if (Test-Path $RegistryPower) {
        Set-ItemProperty -Path $RegistryPower -Name "EventProcessorEnabled" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    # 3. Restaurar throttling e scaling no plano ativo
    Write-Host "[3/4] Reativando Throttling e escala de ociosidade padrao..." -ForegroundColor Yellow
    powercfg -setacvalueindex scheme_current sub_processor THROTTLING 1 2>$null
    powercfg -setacvalueindex scheme_current sub_processor IDLESCALING 0 2>$null
    powercfg /setactive SCHEME_CURRENT 2>$null

    # 4. Restaurar ValueMin de Core Parking para o padrao (geralmente 0, mantido)
    Write-Host "[4/4] Restaurando chaves de Core Parking para o padrao..." -ForegroundColor Yellow
    if (Test-Path $RegistryCoreParkingSettings) {
        Set-ItemProperty -Path $RegistryCoreParkingSettings -Name "ValueMin" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    Write-Host "`n[OK] Ajustes de CPU AMD revertidos para o padrao do Windows com sucesso!" -ForegroundColor Green
}
