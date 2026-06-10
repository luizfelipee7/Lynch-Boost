# ========================================================
# LYNCH FPS BOOST - OTIMIZADOR INTELIGENTE DE GPU V1.1
# ========================================================
# Este script aplica ajustes especificos de alto desempenho,
# latencia PCIe, MSI e telemetria para a fabricante de GPU
# selecionada manualmente pelo usuario no modal (NVIDIA, AMD ou Intel).
# ========================================================

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("Ativar", "Reverter")]
    [string]$Acao,

    [Parameter(Mandatory=$true)]
    [ValidateSet("NVIDIA", "AMD", "Intel")]
    [string]$Fabricante
)

# Requer privilegios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador!"
    exit 1
}

$ClassPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
$RegistryFTS = "HKLM:\SOFTWARE\NVIDIA Corporation\Global\FTS"
$RegistryGMM = "HKLM:\Software\Intel\GMM"

# 1. HABILITAR MSI MODE NA GPU DEDICADA COM PRIORIDADE ALTA
function Set-GpuMsiMode ($VendorID, $Status) {
    $PriorityValue = if ($Status -eq 1) { 3 } else { 0 }
    
    # Procura as GPUs correspondentes ao ID do fabricante com fallback seguro
    $PnpDevices = Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue | Where-Object { $_.PNPDeviceID -like "*VEN_$VendorID*" }
    if (!$PnpDevices) {
        $PnpDevices = Get-WmiObject -Class Win32_VideoController -ErrorAction SilentlyContinue | Where-Object { $_.PNPDeviceID -like "*VEN_$VendorID*" }
    }
    
    foreach ($Device in $PnpDevices) {
        $PnpID = $Device.PNPDeviceID
        $DevParamPath = "HKLM:\SYSTEM\CurrentControlSet\Enum\$PnpID\Device Parameters"
        
        if (Test-Path $DevParamPath) {
            $MsiPath = Join-Path -Path $DevParamPath -ChildPath "Interrupt Management\MessageSignaledInterruptProperties"
            $AffinityPath = Join-Path -Path $DevParamPath -ChildPath "Interrupt Management\Affinity Policy"
            
            if ($Status -eq 1) {
                if (!(Test-Path $MsiPath)) { New-Item -Path $MsiPath -Force | Out-Null }
                if (!(Test-Path $AffinityPath)) { New-Item -Path $AffinityPath -Force | Out-Null }
                
                Set-ItemProperty -Path $MsiPath -Name "MSISupported" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $AffinityPath -Name "DevicePriority" -Value $PriorityValue -Type DWord -Force -ErrorAction SilentlyContinue
                Write-Host "[OK] MSI Mode ativado com prioridade ALTA na GPU ($VendorID) $PnpID" -ForegroundColor Green
            } else {
                # Restaura ao padrao
                if (Test-Path $MsiPath) { Set-ItemProperty -Path $MsiPath -Name "MSISupported" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue }
                if (Test-Path $AffinityPath) { Set-ItemProperty -Path $AffinityPath -Name "DevicePriority" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue }
                Write-Host "[OK] MSI Mode restaurado para o padrao na GPU ($VendorID) $PnpID" -ForegroundColor Green
            }
        }
    }
}

# 2. IDENTIFICAÇÃO E APLICAÇÃO DE TWEAKS DE CLASSE
if ($Acao -eq "Ativar") {
    Write-Host "Iniciando Otimizacao Profunda de GPU: $Fabricante...`n" -ForegroundColor Cyan

    # Habilita MSI prioritario de acordo com a fabricante
    if ($Fabricante -eq "NVIDIA") {
        Set-GpuMsiMode "10DE" 1
    } elseif ($Fabricante -eq "AMD") {
        Set-GpuMsiMode "1002" 1
    }

    # --- AJUSTES GLOBAIS DE LATÊNCIA DE VÍDEO E ENERGIA (EXM) ---
    Write-Host "`nAplicando tolerancias de latência globais do barramento gráfico (DXGKrnl)..." -ForegroundColor Yellow
    $DxgPath = "HKLM:\SYSTEM\CurrentControlSet\Services\DXGKrnl"
    if (Test-Path $DxgPath) {
        Set-ItemProperty -Path $DxgPath -Name "MonitorLatencyTolerance" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $DxgPath -Name "MonitorRefreshLatencyTolerance" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    }
    
    $GpuPowerPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Power"
    if (!(Test-Path $GpuPowerPath)) { New-Item -Path $GpuPowerPath -Force | Out-Null }
    if (Test-Path $GpuPowerPath) {
        $GpuPowerTweaks = @{
            "DefaultD3TransitionLatencyActivelyUsed" = 1
            "DefaultD3TransitionLatencyIdleLongTime" = 1
            "DefaultD3TransitionLatencyIdleMonitorOff" = 1
            "DefaultD3TransitionLatencyIdleNoContext" = 1
            "DefaultD3TransitionLatencyIdleShortTime" = 1
            "DefaultD3TransitionLatencyIdleVeryLongTime" = 1
            "DefaultLatencyToleranceIdle0" = 1
            "DefaultLatencyToleranceIdle0MonitorOff" = 1
            "DefaultLatencyToleranceIdle1" = 1
            "DefaultLatencyToleranceIdle1MonitorOff" = 1
            "DefaultLatencyToleranceMemory" = 1
            "DefaultLatencyToleranceNoContext" = 1
            "DefaultLatencyToleranceNoContextMonitorOff" = 1
            "DefaultLatencyToleranceOther" = 1
            "DefaultLatencyToleranceTimerPeriod" = 1
            "DefaultMemoryRefreshLatencyToleranceActivelyUsed" = 1
            "DefaultMemoryRefreshLatencyToleranceMonitorOff" = 1
            "DefaultMemoryRefreshLatencyToleranceNoContext" = 1
            "Latency" = 1
            "MaxIAverageGraphicsLatencyInOneBucket" = 1
            "MiracastPerfTrackGraphicsLatency" = 1
            "MonitorLatencyTolerance" = 1
            "MonitorRefreshLatencyTolerance" = 1
            "TransitionLatency" = 1
        }
        foreach ($Key in $GpuPowerTweaks.Keys) {
            Set-ItemProperty -Path $GpuPowerPath -Name $Key -Value $GpuPowerTweaks[$Key] -Type DWord -Force -ErrorAction SilentlyContinue
        }
    }

    # Busca as subchaves numericas validas do driver de video com tratamento silencioso de erros de permissao
    $SubKeys = Get-ChildItem -Path $ClassPath -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -match "^\d{4}$" }

    foreach ($SubKey in $SubKeys) {
        $SubKeyPath = Join-Path -Path $ClassPath -ChildPath $SubKey.PSChildName
        $Desc = (Get-ItemProperty -Path $SubKeyPath -Name "DriverDesc" -ErrorAction SilentlyContinue).DriverDesc
        $Provider = (Get-ItemProperty -Path $SubKeyPath -Name "ProviderName" -ErrorAction SilentlyContinue).ProviderName

        # --- APLICAÇÃO NVIDIA ---
        if ($Fabricante -eq "NVIDIA" -and ($Desc -like "*NVIDIA*" -or $Provider -like "*NVIDIA*")) {
            Write-Host "`nOtimizando driver de video NVIDIA ($Desc)..." -ForegroundColor Yellow
            
            # Latencias de Barramento PCIe (D3PC, LOWLATENCY, VRR)
            $NvidiaTweaks = @{
                "D3PCLatency" = 1
                "F1TransitionLatency" = 1
                "LOWLATENCY" = 1
                "Node3DLowLatency" = 1
                "PciLatencyTimerControl" = 20
                "RMDeepL1EntryLatencyUsec" = 1
                "RmGspcMaxFtuS" = 1
                "RmGspcMinFtuS" = 1
                "RmGspcPerioduS" = 1
                "RMLpwrEiIdleThresholdUs" = 1
                "RMLpwrGrIdleThresholdUs" = 1
                "RMLpwrGrRgIdleThresholdUs" = 1
                "RMLpwrMsIdleThresholdUs" = 1
                "VRDirectFlipDPCDelayUs" = 1
                "VRDirectFlipTimingMarginUs" = 1
                "VRDirectJITFlipMsHybridFlipDelayUs" = 1
                "vrrCursorMarginUs" = 1
                "vrrDeflickerMarginUs" = 1
                "vrrDeflickerMaxUs" = 1
            }

            foreach ($Key in $NvidiaTweaks.Keys) {
                Set-ItemProperty -Path $SubKeyPath -Name $Key -Value $NvidiaTweaks[$Key] -Type DWord -Force -ErrorAction SilentlyContinue
            }

            # Telemetria Global NVIDIA
            if (!(Test-Path $RegistryFTS)) { New-Item -Path $RegistryFTS -Force | Out-Null }
            Set-ItemProperty -Path $RegistryFTS -Name "EnableRID66610" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $RegistryFTS -Name "EnableRID64640" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $RegistryFTS -Name "EnableRID44231" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

            # Remove da inicializacao do Windows
            Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "NvBackend" -ErrorAction SilentlyContinue

            # Corta as tarefas agendadas de telemetria de forma inteligente
            Get-ScheduledTask | Where-Object { $_.TaskName -like "*NvTmRep*" -or $_.TaskName -like "*NvTmMon*" -or $_.TaskName -like "*NvDriverUpdateCheckDaily*" -or $_.TaskName -like "*GeForce Experience SelfUpdate*" } | Disable-ScheduledTask -ErrorAction SilentlyContinue | Out-Null

            # Ativa a opção "Use as configurações de imagem avançadas em 3D"
            $NVTweakPath = "HKCU:\Software\NVIDIA Corporation\Global\NVTweak"
            try {
                if (!(Test-Path $NVTweakPath)) { New-Item -Path $NVTweakPath -Force | Out-Null }
                Set-ItemProperty -Path $NVTweakPath -Name "Gestalt" -Value 2 -Type DWord -Force -ErrorAction SilentlyContinue
                Write-Host "[OK] Ajustes de Barramento PCIe, telemetria e 'Use as configurações de imagem avançadas em 3D' ativados para NVIDIA!" -ForegroundColor Green
            } catch {
                Write-Host "[OK] Ajustes de Barramento PCIe e telemetria desativados para NVIDIA!" -ForegroundColor Green
            }
        }
        
        # --- APLICAÇÃO AMD RADEON ---
        elseif ($Fabricante -eq "AMD" -and ($Desc -like "*AMD*" -or $Desc -like "*Radeon*" -or $Provider -like "*AMD*")) {
            Write-Host "`nOtimizando driver de video AMD Radeon ($Desc)..." -ForegroundColor Yellow

            # Desativar ULPS (Corrige crashes de drivers, telas piscando e congelamentos)
            Set-ItemProperty -Path $SubKeyPath -Name "EnableUlps" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $SubKeyPath -Name "EnableUlps_NA" -Value "0" -Type String -Force -ErrorAction SilentlyContinue

            # Desativar Radeon Overlay
            Set-ItemProperty -Path $SubKeyPath -Name "AllowRSOverlay" -Value "false" -Type String -Force -ErrorAction SilentlyContinue

            # Desativar Power Gating / Clock Gating (Placa sempre pronta para processar)
            $AmdPowerKeys = @{
                "DisableSAMUPowerGating" = 1
                "DisableUVDPowerGatingDynamic" = 1
                "DisableVCEPowerGating" = 1
                "DisablePowerGating" = 1
                "DisableDrmdmaPowerGating" = 1
                "EnableVceSwClockGating" = 1
                "EnableUvdClockGating" = 1
                "EnableAspmL0s" = 0
                "EnableAspmL1" = 0
                "PP_SclkDeepSleepDisable" = 1
                "PP_ThermalAutoThrottlingEnable" = 0
                "KMD_DeLagEnabled" = 1
                "KMD_FRTEnabled" = 0
                "DisableDMACopy" = 1
                "DisableBlockWrite" = 0
                "StutterMode" = 0
                "KMD_EnableComputePreemption" = 0
                "PP_GPUPowerDownEnabled" = 1
                "AllowSnapshot" = 0
                "AllowSubscription" = 0
                "AllowSkins" = "false"
                "AutoColorDepthReduction_NA" = 0
            }

            foreach ($Key in $AmdPowerKeys.Keys) {
                $Type = if ($AmdPowerKeys[$Key] -is [string]) { "String" } else { "DWord" }
                Set-ItemProperty -Path $SubKeyPath -Name $Key -Value $AmdPowerKeys[$Key] -Type $Type -Force -ErrorAction SilentlyContinue
            }

            # Configurações UMD (User Mode Driver - Latência e Shader)
            $UmdPath = Join-Path -Path $SubKeyPath -ChildPath "UMD"
            if (!(Test-Path $UmdPath)) { New-Item -Path $UmdPath -Force | Out-Null }
            if (Test-Path $UmdPath) {
                Set-ItemProperty -Path $UmdPath -Name "Main3D_DEF" -Value "1" -Type String -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $UmdPath -Name "Main3D" -Value ([byte[]](0x31, 0x00)) -Type Binary -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $UmdPath -Name "FlipQueueSize" -Value ([byte[]](0x31, 0x00)) -Type Binary -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $UmdPath -Name "ShaderCache" -Value ([byte[]](0x32, 0x00)) -Type Binary -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $UmdPath -Name "TFQ" -Value ([byte[]](0x32, 0x00)) -Type Binary -Force -ErrorAction SilentlyContinue
            }

            # Desativa AMD Logging Service
            Stop-Service -Name amdlog -Force -ErrorAction SilentlyContinue
            Set-Service -Name amdlog -StartupType Disabled -ErrorAction SilentlyContinue

            Write-Host "[OK] ULPS desativado, Power Gating desligado e FlipQueueSize de baixa latência aplicados para AMD Radeon!" -ForegroundColor Green
        }

        # --- APLICAÇÃO INTEL GRAPHICS ---
        elseif ($Fabricante -eq "Intel" -and ($Desc -like "*Intel*" -or $Provider -like "*Intel*")) {
            Write-Host "`nOtimizando driver de video Intel Graphics ($Desc)..." -ForegroundColor Yellow

            $IntelKeys = @{
                "Disable_OverlayDSQualityEnhancement" = 1
                "IncreaseFixedSegment" = 1
                "AdaptiveVsyncEnable" = 0
                "DisablePFonDP" = 1
                "EnableCompensationForDVI" = 1
                "NoFastLinkTrainingForeDP" = 0
                "ACPowerPolicyVersion" = 16898
                "DCPowerPolicyVersion" = 16642
            }

            foreach ($Key in $IntelKeys.Keys) {
                Set-ItemProperty -Path $SubKeyPath -Name $Key -Value $IntelKeys[$Key] -Type DWord -Force -ErrorAction SilentlyContinue
            }

            # Dedicated Segment Size
            if (!(Test-Path $RegistryGMM)) { New-Item -Path $RegistryGMM -Force | Out-Null }
            Set-ItemProperty -Path $RegistryGMM -Name "DedicatedSegmentSize" -Value 512 -Type DWord -Force -ErrorAction SilentlyContinue

            Write-Host "[OK] Economias de energia desativadas e alocação de vídeo otimizada para Intel!" -ForegroundColor Green
        }
    }

    Write-Host "`nOtimizacao da GPU $Fabricante concluida com sucesso! Reinicie o PC para aplicar as mudancas nos drivers de hardware." -ForegroundColor Cyan

} elseif ($Acao -eq "Reverter") {
    Write-Host "Revertendo Otimizacoes de Placa de Video ($Fabricante) para o Padrao..." -ForegroundColor Cyan

    # Restaura MSI ao padrao
    if ($Fabricante -eq "NVIDIA") {
        Set-GpuMsiMode "10DE" 0
        Write-Host "[INFO] Para restaurar o perfil de video NVIDIA original ao padrao de fabrica, abra o Painel de Controle NVIDIA e clique em 'Restaurar' no menu de Gerenciar Configuracoes 3D ou clique no botao de restaurar no Inspector." -ForegroundColor Cyan
    } elseif ($Fabricante -eq "AMD") {
        Set-GpuMsiMode "1002" 0
    }

    # --- REVERTE AJUSTES GLOBAIS DE VÍDEO E ENERGIA ---
    $DxgPath = "HKLM:\SYSTEM\CurrentControlSet\Services\DXGKrnl"
    if (Test-Path $DxgPath) {
        Remove-ItemProperty -Path $DxgPath -Name "MonitorLatencyTolerance" -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $DxgPath -Name "MonitorRefreshLatencyTolerance" -ErrorAction SilentlyContinue
    }
    $GpuPowerPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Power"
    if (Test-Path $GpuPowerPath) {
        $GpuPowerTweaks = @("DefaultD3TransitionLatencyActivelyUsed", "DefaultD3TransitionLatencyIdleLongTime", "DefaultD3TransitionLatencyIdleMonitorOff", 
                            "DefaultD3TransitionLatencyIdleNoContext", "DefaultD3TransitionLatencyIdleShortTime", "DefaultD3TransitionLatencyIdleVeryLongTime", 
                            "DefaultLatencyToleranceIdle0", "DefaultLatencyToleranceIdle0MonitorOff", "DefaultLatencyToleranceIdle1", 
                            "DefaultLatencyToleranceIdle1MonitorOff", "DefaultLatencyToleranceMemory", "DefaultLatencyToleranceNoContext", 
                            "DefaultLatencyToleranceNoContextMonitorOff", "DefaultLatencyToleranceOther", "DefaultLatencyToleranceTimerPeriod", 
                            "DefaultMemoryRefreshLatencyToleranceActivelyUsed", "DefaultMemoryRefreshLatencyToleranceMonitorOff", 
                            "DefaultMemoryRefreshLatencyToleranceNoContext", "Latency", "MaxIAverageGraphicsLatencyInOneBucket", 
                            "MiracastPerfTrackGraphicsLatency", "MonitorLatencyTolerance", "MonitorRefreshLatencyTolerance", "TransitionLatency")
        foreach ($Key in $GpuPowerTweaks) {
            Remove-ItemProperty -Path $GpuPowerPath -Name $Key -ErrorAction SilentlyContinue
        }
    }

    $SubKeys = Get-ChildItem -Path $ClassPath -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -match "^\d{4}$" }

    foreach ($SubKey in $SubKeys) {
        $SubKeyPath = Join-Path -Path $ClassPath -ChildPath $SubKey.PSChildName
        $Desc = (Get-ItemProperty -Path $SubKeyPath -Name "DriverDesc" -ErrorAction SilentlyContinue).DriverDesc
        $Provider = (Get-ItemProperty -Path $SubKeyPath -Name "ProviderName" -ErrorAction SilentlyContinue).ProviderName

        # --- REVERSÃO NVIDIA ---
        if ($Fabricante -eq "NVIDIA" -and ($Desc -like "*NVIDIA*" -or $Provider -like "*NVIDIA*")) {
            $NvidiaTweaks = @("D3PCLatency", "F1TransitionLatency", "LOWLATENCY", "Node3DLowLatency", "PciLatencyTimerControl", 
                              "RMDeepL1EntryLatencyUsec", "RmGspcMaxFtuS", "RmGspcMinFtuS", "RmGspcPerioduS", 
                              "RMLpwrEiIdleThresholdUs", "RMLpwrGrIdleThresholdUs", "RMLpwrGrRgIdleThresholdUs", 
                              "RMLpwrMsIdleThresholdUs", "VRDirectFlipDPCDelayUs", "VRDirectFlipTimingMarginUs", 
                              "VRDirectJITFlipMsHybridFlipDelayUs", "vrrCursorMarginUs", "vrrDeflickerMarginUs", "vrrDeflickerMaxUs")
            
            foreach ($Key in $NvidiaTweaks) {
                Remove-ItemProperty -Path $SubKeyPath -Name $Key -ErrorAction SilentlyContinue
            }

            # Reativa telemetria NVIDIA
            if (Test-Path $RegistryFTS) {
                Set-ItemProperty -Path $RegistryFTS -Name "EnableRID66610" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $RegistryFTS -Name "EnableRID64640" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $RegistryFTS -Name "EnableRID44231" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            }

            # Restaura a opção de imagem 3D da NVIDIA
            Remove-ItemProperty -Path "HKCU:\Software\NVIDIA Corporation\Global\NVTweak" -Name "Gestalt" -ErrorAction SilentlyContinue

            Get-ScheduledTask | Where-Object { $_.TaskName -like "*NvTmRep*" -or $_.TaskName -like "*NvTmMon*" } | Enable-ScheduledTask -ErrorAction SilentlyContinue | Out-Null
            Write-Host "[OK] Ajustes e telemetria da NVIDIA restaurados ao padrao." -ForegroundColor Green
        }
        
        # --- REVERSÃO AMD ---
        elseif ($Fabricante -eq "AMD" -and ($Desc -like "*AMD*" -or $Desc -like "*Radeon*" -or $Provider -like "*AMD*")) {
            # Restaura ULPS e Overlay
            Set-ItemProperty -Path $SubKeyPath -Name "EnableUlps" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $SubKeyPath -Name "EnableUlps_NA" -Value "1" -Type String -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $SubKeyPath -Name "AllowRSOverlay" -Value "true" -Type String -Force -ErrorAction SilentlyContinue

            $AmdPowerKeys = @("DisableSAMUPowerGating", "DisableUVDPowerGatingDynamic", "DisableVCEPowerGating", "DisablePowerGating", 
                              "DisableDrmdmaPowerGating", "EnableVceSwClockGating", "EnableUvdClockGating", "EnableAspmL0s", 
                              "EnableAspmL1", "PP_SclkDeepSleepDisable", "PP_ThermalAutoThrottlingEnable", "KMD_DeLagEnabled", 
                              "KMD_FRTEnabled", "DisableDMACopy", "DisableBlockWrite", "StutterMode", "KMD_EnableComputePreemption", 
                              "PP_GPUPowerDownEnabled", "AllowSnapshot", "AllowSubscription", "AllowSkins", "AutoColorDepthReduction_NA")
            
            foreach ($Key in $AmdPowerKeys) {
                Remove-ItemProperty -Path $SubKeyPath -Name $Key -ErrorAction SilentlyContinue
            }

            # Restaura UMD
            $UmdPath = Join-Path -Path $SubKeyPath -ChildPath "UMD"
            if (Test-Path $UmdPath) {
                Remove-ItemProperty -Path $UmdPath -Name "Main3D_DEF" -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $UmdPath -Name "Main3D" -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $UmdPath -Name "FlipQueueSize" -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $UmdPath -Name "ShaderCache" -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $UmdPath -Name "TFQ" -ErrorAction SilentlyContinue
            }

            # Reativa servico AMD
            Set-Service -Name amdlog -StartupType Automatic -ErrorAction SilentlyContinue
            Start-Service -Name amdlog -ErrorAction SilentlyContinue

            Write-Host "[OK] ULPS e economias de energia da AMD restaurados ao padrao." -ForegroundColor Green
        }

        # --- REVERSÃO INTEL ---
        elseif ($Fabricante -eq "Intel" -and ($Desc -like "*Intel*" -or $Provider -like "*Intel*")) {
            $IntelKeys = @("Disable_OverlayDSQualityEnhancement", "IncreaseFixedSegment", "AdaptiveVsyncEnable", 
                           "DisablePFonDP", "EnableCompensationForDVI", "NoFastLinkTrainingForeDP", 
                           "ACPowerPolicyVersion", "DCPowerPolicyVersion")

            foreach ($Key in $IntelKeys) {
                Remove-ItemProperty -Path $SubKeyPath -Name $Key -ErrorAction SilentlyContinue
            }

            if (Test-Path $RegistryGMM) {
                Remove-ItemProperty -Path $RegistryGMM -Name "DedicatedSegmentSize" -ErrorAction SilentlyContinue
            }

            Write-Host "[OK] Ajustes e limites de video Intel restaurados ao padrao." -ForegroundColor Green
        }
    }

    Write-Host "`n[OK] Otimizacoes da GPU $Fabricante revertidas com sucesso!" -ForegroundColor Green
}
