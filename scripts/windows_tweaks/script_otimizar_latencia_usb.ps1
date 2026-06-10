# ========================================================
# LYNCH FPS BOOST - OTIMIZAÇÃO DE LATÊNCIA USB & MSI MODE
# ========================================================
# Este script otimiza a latência física dos barramentos USB.
# Ele desativa a suspensão seletiva e economias de energia,
# ativa o MSI Mode nos controladores e prioriza os drivers.
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

$RegistryServices = "HKLM:\SYSTEM\CurrentControlSet\Services"
$RegistryEnum = "HKLM:\SYSTEM\CurrentControlSet\Enum"

# Lista de drivers para ajuste de prioridade de Thread
$DriversPrioritarios = @("usbxhci", "USBHUB3", "nvlddmkm", "NDIS")

if ($Acao -eq "Ativar") {
    Write-Host "Ativando Otimizacoes de Latencia USB..." -ForegroundColor Cyan

    # 1. Obter controladores USB físicos ativos (PCI)
    Write-Host "[1/4] Varrendo controladores USB físicos ativos (PCI)..." -ForegroundColor Yellow
    $Controllers = Get-CimInstance Win32_USBController -ErrorAction SilentlyContinue | Where-Object { $_.PNPDeviceID -like "*PCI\VEN_*" }
    if (!$Controllers) {
        $Controllers = Get-WmiObject -Class Win32_USBController -ErrorAction SilentlyContinue | Where-Object { $_.PNPDeviceID -like "*PCI\VEN_*" }
    }

    if ($Controllers) {
        foreach ($Dev in $Controllers) {
            $PnpID = $Dev.PNPDeviceID
            $DevParamPath = "$RegistryEnum\$PnpID\Device Parameters"

            if (Test-Path $DevParamPath) {
                Write-Host " -> Desativando economia de energia para: $PnpID" -ForegroundColor Green
                Set-ItemProperty -Path $DevParamPath -Name "AllowIdleIrpInD3" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $DevParamPath -Name "D3ColdSupported" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $DevParamPath -Name "DeviceSelectiveSuspended" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $DevParamPath -Name "EnableSelectiveSuspend" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $DevParamPath -Name "EnhancedPowerManagementEnabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $DevParamPath -Name "SelectiveSuspendEnabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $DevParamPath -Name "SelectiveSuspendOn" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
            }

            # 2. Configurar MSI Mode para latência estável de polling rate
            $MsiPath = "$DevParamPath\Interrupt Management\MessageSignaledInterruptProperties"
            if (!(Test-Path $MsiPath)) {
                New-Item -Path $MsiPath -Force | Out-Null
            }
            Set-ItemProperty -Path $MsiPath -Name "MSISupported" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue

            # Limpar prioridade de afinidade antiga se houver
            $AffinityPath = "$DevParamPath\Interrupt Management\Affinity Policy"
            if (Test-Path $AffinityPath) {
                Remove-ItemProperty -Path $AffinityPath -Name "DevicePriority" -ErrorAction SilentlyContinue | Out-Null
            }
        }
    } else {
        Write-Host " -> Nenhum controlador PCI USB encontrado." -ForegroundColor Yellow
    }

    # 3. Elevar prioridades de Thread dos drivers essenciais
    Write-Host "[2/4] Elevando ThreadPriority dos drivers essenciais..." -ForegroundColor Yellow
    foreach ($Drv in $DriversPrioritarios) {
        $ParamPath = "$RegistryServices\$Drv\Parameters"
        if (!(Test-Path $ParamPath)) {
            New-Item -Path $ParamPath -Force | Out-Null
        }
        Set-ItemProperty -Path $ParamPath -Name "ThreadPriority" -Value 31 -Type DWord -Force -ErrorAction SilentlyContinue
        Write-Host " -> ThreadPriority de '$Drv' definido para 31 (Realtime)." -ForegroundColor Green
    }

    # 4. Desativar Selective Suspend Global
    Write-Host "[3/4] Desativando Suspensão Seletiva USB global..." -ForegroundColor Yellow
    $UsbGlobalPath = "$RegistryServices\USB"
    if (!(Test-Path $UsbGlobalPath)) {
        New-Item -Path $UsbGlobalPath -Force | Out-Null
    }
    Set-ItemProperty -Path $UsbGlobalPath -Name "DisableSelectiveSuspend" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue

    Write-Host "`n[OK] Otimizacoes de latencia USB aplicadas com sucesso!" -ForegroundColor Green

} elseif ($Acao -eq "Reverter") {
    Write-Host "Revertendo Otimizacoes de Latencia USB..." -ForegroundColor Cyan

    # 1. Reverter economia de energia e MSI nos controladores
    Write-Host "[1/4] Restaurando gerenciamento de energia dos controladores USB..." -ForegroundColor Yellow
    $Controllers = Get-CimInstance Win32_USBController -ErrorAction SilentlyContinue | Where-Object { $_.PNPDeviceID -like "*PCI\VEN_*" }
    if (!$Controllers) {
        $Controllers = Get-WmiObject -Class Win32_USBController -ErrorAction SilentlyContinue | Where-Object { $_.PNPDeviceID -like "*PCI\VEN_*" }
    }

    if ($Controllers) {
        foreach ($Dev in $Controllers) {
            $PnpID = $Dev.PNPDeviceID
            $DevParamPath = "$RegistryEnum\$PnpID\Device Parameters"

            if (Test-Path $DevParamPath) {
                # Remover propriedades customizadas de economia
                Remove-ItemProperty -Path $DevParamPath -Name "AllowIdleIrpInD3" -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $DevParamPath -Name "D3ColdSupported" -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $DevParamPath -Name "DeviceSelectiveSuspended" -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $DevParamPath -Name "EnableSelectiveSuspend" -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $DevParamPath -Name "EnhancedPowerManagementEnabled" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $DevParamPath -Name "SelectiveSuspendEnabled" -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $DevParamPath -Name "SelectiveSuspendOn" -ErrorAction SilentlyContinue
            }

            # Reverter MSI Mode
            $MsiPath = "$DevParamPath\Interrupt Management\MessageSignaledInterruptProperties"
            if (Test-Path $MsiPath) {
                Remove-ItemProperty -Path $MsiPath -Name "MSISupported" -ErrorAction SilentlyContinue
            }
        }
    }

    # 2. Restaurar ThreadPriority dos drivers padrão do Windows
    Write-Host "[2/4] Restaurando prioridade de Thread dos drivers..." -ForegroundColor Yellow
    foreach ($Drv in $DriversPrioritarios) {
        $ParamPath = "$RegistryServices\$Drv\Parameters"
        if (Test-Path $ParamPath) {
            Remove-ItemProperty -Path $ParamPath -Name "ThreadPriority" -ErrorAction SilentlyContinue
            Write-Host " -> ThreadPriority de '$Drv' restaurado ao padrao." -ForegroundColor Green
        }
    }

    # 3. Remover suspensão seletiva USB global
    Write-Host "[3/4] Reativando Suspensão Seletiva USB global..." -ForegroundColor Yellow
    $UsbGlobalPath = "$RegistryServices\USB"
    if (Test-Path $UsbGlobalPath) {
        Remove-ItemProperty -Path $UsbGlobalPath -Name "DisableSelectiveSuspend" -ErrorAction SilentlyContinue
    }

    Write-Host "`n[OK] Otimizacoes de latencia USB revertidas para o padrao!" -ForegroundColor Green
}
