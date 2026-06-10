# ========================================================
# LYNCH FPS BOOST - REDUÇÃO GLOBAL DE LATÊNCIA (PING/HW) V1.2
# ========================================================
# Este script otimiza as interrupções de hardware, clocks,
# e aplica melhorias na camada física dos adaptadores de rede,
# desabilitando economia de energia e moderação de latência.
# ========================================================

# Requer privilégios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador!"
    exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   LYNCH FPS BOOST - REDUCAO GLOBAL DE LATENCIA (PING/HW)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# [1/4] Maximizando Alocação de Memória RAM para Jogos (FSUTIL)
Write-Host "[1/4] Maximizando alocacao de memoria RAM (FSUTIL)..." -ForegroundColor Yellow
try {
    fsutil behavior set memoryusage 2 | Out-Null
    Write-Host "[OK] O Windows agora usara mais RAM para cache de sistema e jogos pesados!" -ForegroundColor Green
} catch {
    Write-Warning "Falha ao definir FSUTIL memoryusage."
}
Write-Host ""

# [2/4] Reduzindo Latência de Entrada do Sistema (BCDEDIT)
Write-Host "[2/4] Desativando relogios dinamicos de economia de energia (BCDEDIT)..." -ForegroundColor Yellow
try {
    bcdedit /set useplatformtick yes 2>$null | Out-Null
    bcdedit /set disabledynamictick yes 2>$null | Out-Null
    Write-Host "[OK] Relogios dinamicos desativados com sucesso!" -ForegroundColor Green
} catch {
    Write-Warning "Falha ao definir BCDEDIT."
}
Write-Host ""

# [3/4] Otimizando Rede TCP/IP & MMCSS (Redução de Ping e Latência de Rede)
Write-Host "[3/4] Otimizando rede TCP/IP e politicas MMCSS..." -ForegroundColor Yellow

# Desativar Algoritmo de Nagle em todas as interfaces de rede
$InterfacesPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
if (Test-Path $InterfacesPath) {
    Get-ChildItem -Path $InterfacesPath -ErrorAction SilentlyContinue | ForEach-Object {
        Set-ItemProperty -Path $_.PSPath -Name "TcpAckFrequency" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $_.PSPath -Name "TCPNoDelay" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    }
}

# Desativar Network Throttling e priorizar responsividade
$SystemProfilePath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
if (!(Test-Path $SystemProfilePath)) { New-Item -Path $SystemProfilePath -Force | Out-Null }
Set-ItemProperty -Path $SystemProfilePath -Name "NetworkThrottlingIndex" -Value 0xffffffff -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $SystemProfilePath -Name "SystemResponsiveness" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

# Otimizar DNS e prioridades do Provedor de Internet
$ServiceProviderPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\ServiceProvider"
if (Test-Path $ServiceProviderPath) {
    Set-ItemProperty -Path $ServiceProviderPath -Name "LocalPriority" -Value 4 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $ServiceProviderPath -Name "HostsPriority" -Value 5 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $ServiceProviderPath -Name "DnsPriority" -Value 6 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $ServiceProviderPath -Name "NetbtPriority" -Value 7 -Type DWord -Force -ErrorAction SilentlyContinue
}

# Otimizar MMCSS para tarefas de baixa latência e jogos
$TasksPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks"

$LowLatencyPath = "$TasksPath\Low Latency"
if (!(Test-Path $LowLatencyPath)) { New-Item -Path $LowLatencyPath -Force | Out-Null }
Set-ItemProperty -Path $LowLatencyPath -Name "Affinity" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $LowLatencyPath -Name "Background Only" -Value "False" -Type String -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $LowLatencyPath -Name "BackgroundPriority" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $LowLatencyPath -Name "Clock Rate" -Value 10000 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $LowLatencyPath -Name "GPU Priority" -Value 8 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $LowLatencyPath -Name "Priority" -Value 2 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $LowLatencyPath -Name "Scheduling Category" -Value "Medium" -Type String -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $LowLatencyPath -Name "SFIO Priority" -Value "High" -Type String -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $LowLatencyPath -Name "Latency Sensitive" -Value "True" -Type String -Force -ErrorAction SilentlyContinue

$GamesPath = "$TasksPath\Games"
if (!(Test-Path $GamesPath)) { New-Item -Path $GamesPath -Force | Out-Null }
Set-ItemProperty -Path $GamesPath -Name "Affinity" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $GamesPath -Name "Background Only" -Value "False" -Type String -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $GamesPath -Name "BackgroundPriority" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $GamesPath -Name "Clock Rate" -Value 10000 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $GamesPath -Name "GPU Priority" -Value 18 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $GamesPath -Name "Priority" -Value 2 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $GamesPath -Name "Scheduling Category" -Value "High" -Type String -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $GamesPath -Name "SFIO Priority" -Value "High" -Type String -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $GamesPath -Name "Latency Sensitive" -Value "True" -Type String -Force -ErrorAction SilentlyContinue

Write-Host "[OK] Algoritmo de Nagle desativado e MMCSS configurado!" -ForegroundColor Green
Write-Host ""

# [4/4] Otimizando Adaptadores de Rede Físicos (Offloading e Power Saving de Hardware)
Write-Host "[4/4] Aplicando melhorias fisicas nos adaptadores de rede (Offloading & Power Saving)..." -ForegroundColor Yellow

# Ajustar configuracoes TCP locais e globais
Set-NetTCPSetting -SettingName internet -EcnCapability disabled -ErrorAction SilentlyContinue | Out-Null
Set-NetOffloadGlobalSetting -Chimney disabled -ErrorAction SilentlyContinue | Out-Null
Set-NetTCPSetting -SettingName internet -Timestamps disabled -ErrorAction SilentlyContinue | Out-Null
Set-NetTCPSetting -SettingName internet -MaxSynRetransmissions 2 -ErrorAction SilentlyContinue | Out-Null
Set-NetTCPSetting -SettingName internet -NonSackRttResiliency disabled -ErrorAction SilentlyContinue | Out-Null
Set-NetTCPSetting -SettingName internet -InitialRto 2000 -ErrorAction SilentlyContinue | Out-Null
Set-NetTCPSetting -SettingName internet -MinRto 300 -ErrorAction SilentlyContinue | Out-Null
Set-NetTCPSetting -SettingName Internet -AutoTuningLevelLocal normal -ErrorAction SilentlyContinue | Out-Null
Set-NetTCPSetting -SettingName internet -ScalingHeuristics disabled -ErrorAction SilentlyContinue | Out-Null
if (Get-Command "netsh" -ErrorAction SilentlyContinue) {
    netsh int tcp set supplemental internet congestionprovider=ctcp 2>$null | Out-Null
}
Set-NetOffloadGlobalSetting -ReceiveSegmentCoalescing enabled -ErrorAction SilentlyContinue | Out-Null
Set-NetOffloadGlobalSetting -ReceiveSideScaling enabled -ErrorAction SilentlyContinue | Out-Null

# Desativar LSO (Large Send Offload) e Checksum Offloading para prevenir overhead do chip e bugs de driver
Disable-NetAdapterLso -Name * -ErrorAction SilentlyContinue | Out-Null
Disable-NetAdapterChecksumOffload -Name * -ErrorAction SilentlyContinue | Out-Null

# Desabilitar recursos avançados de economia de energia e atraso de moderação
$AdvancedProperties = @(
    @{ DisplayName = "Energy-Efficient Ethernet"; DisplayValue = "Disabled" },
    @{ DisplayName = "Energy Efficient Ethernet"; DisplayValue = "Disabled" },
    @{ DisplayName = "Energy Efficient Ethernet"; DisplayValue = "Off" },
    @{ DisplayName = "Ultra Low Power Mode"; DisplayValue = "Disabled" },
    @{ DisplayName = "System Idle Power Saver"; DisplayValue = "Disabled" },
    @{ DisplayName = "Green Ethernet"; DisplayValue = "Disabled" },
    @{ DisplayName = "Power Saving Mode"; DisplayValue = "Disabled" },
    @{ DisplayName = "Gigabit Lite"; DisplayValue = "Disabled" },
    @{ DisplayName = "EEE"; DisplayValue = "Disabled" },
    @{ DisplayName = "Advanced EEE"; DisplayValue = "Disabled" },
    @{ DisplayName = "ARP Offload"; DisplayValue = "Disabled" },
    @{ DisplayName = "NS Offload"; DisplayValue = "Disabled" },
    @{ DisplayName = "Idle Power Saving"; DisplayValue = "Disabled" },
    @{ DisplayName = "Flow Control"; DisplayValue = "Disabled" },
    @{ DisplayName = "Interrupt Moderation"; DisplayValue = "Disabled" },
    @{ DisplayName = "Reduce Speed On Power Down"; DisplayValue = "Disabled" },
    @{ DisplayName = "Interrupt Moderation Rate"; DisplayValue = "Off" }
)

foreach ($Prop in $AdvancedProperties) {
    Set-NetAdapterAdvancedProperty -Name * -DisplayName $Prop.DisplayName -DisplayValue $Prop.DisplayValue -ErrorAction SilentlyContinue | Out-Null
}

# Desabilitar desligamento automático da placa de rede para economizar energia (Desktops apenas)
try {
    if ((Get-CimInstance -ClassName Win32_ComputerSystem -ErrorAction SilentlyContinue).PCSystemType -ne 2) {
        $adapters = Get-NetAdapter -Physical -ErrorAction SilentlyContinue | Get-NetAdapterPowerManagement -ErrorAction SilentlyContinue | Where-Object -FilterScript { $_.AllowComputerToTurnOffDevice -ne "Unsupported" }
        foreach ($adapter in $adapters) {
            $adapter.AllowComputerToTurnOffDevice = "Disabled"
            $adapter | Set-NetAdapterPowerManagement -ErrorAction SilentlyContinue | Out-Null
        }
    }
} catch {
    # Ignora silenciosamente se as APIs de gerenciamento de energia do adaptador não forem suportadas
}

Write-Host "[OK] Ajustes de rede fisica e economia de energia aplicados com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Otimizacao global de latência concluida com sucesso!" -ForegroundColor Cyan
Write-Host "Reinicie o computador para aplicar as alteracoes de hardware." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
exit 0
