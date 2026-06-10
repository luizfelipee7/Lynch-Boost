param([string]$Acao = "Ativar")

# Requer privilegios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$PSCommandPath`" -Acao $Acao" -Verb RunAs
    exit
}

if ($Acao -eq "Ativar") {
    Write-Output "Desativando Game DVR e Gravacao de Clipes em Segundo Plano..."

    # 1. Chaves de Telemetria e Captura do GameDVR (HKCU)
    $GameDVRPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR"
    if (!(Test-Path $GameDVRPath)) { New-Item -Path $GameDVRPath -Force | Out-Null }
    Set-ItemProperty -Path $GameDVRPath -Name "AppCaptureEnabled" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $GameDVRPath -Name "AudioCaptureEnabled" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $GameDVRPath -Name "CursorCaptureEnabled" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $GameDVRPath -Name "HistoricalCaptureEnabled" -Value 0 -Type DWord -Force

    # 2. Chaves da GameBar (HKCU)
    $GameBarPath = "HKCU:\Software\Microsoft\GameBar"
    if (!(Test-Path $GameBarPath)) { New-Item -Path $GameBarPath -Force | Out-Null }
    Set-ItemProperty -Path $GameBarPath -Name "UseNexusForGameBarEnabled" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $GameBarPath -Name "GameDVR_Enabled" -Value 0 -Type DWord -Force

    # 3. Chave do GameConfigStore (HKCU)
    $GameStorePath = "HKCU:\System\GameConfigStore"
    if (Test-Path $GameStorePath) {
        Set-ItemProperty -Path $GameStorePath -Name "GameDVR_Enabled" -Value 0 -Type DWord -Force
    }

    # 4. Politicas de Grupo - GPO (HKLM)
    $GpoPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR"
    if (!(Test-Path $GpoPath)) { New-Item -Path $GpoPath -Force | Out-Null }
    Set-ItemProperty -Path $GpoPath -Name "AllowGameDVR" -Value 0 -Type DWord -Force

    # 5. PolicyManager (HKLM)
    $PolicyPath = "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR"
    if (Test-Path $PolicyPath) {
        Set-ItemProperty -Path $PolicyPath -Name "value" -Value 0 -Type DWord -Force
    }

    Write-Output "[OK] Game DVR e gravacao em segundo plano desativados com sucesso!"
} else {
    Write-Output "Restaurando Game DVR e Gravacao de Clipes do Windows..."

    # 1. Chaves de Telemetria e Captura do GameDVR (HKCU)
    $GameDVRPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR"
    if (Test-Path $GameDVRPath) {
        Set-ItemProperty -Path $GameDVRPath -Name "AppCaptureEnabled" -Value 1 -Type DWord -Force
        Set-ItemProperty -Path $GameDVRPath -Name "AudioCaptureEnabled" -Value 1 -Type DWord -Force
        Set-ItemProperty -Path $GameDVRPath -Name "CursorCaptureEnabled" -Value 1 -Type DWord -Force
        Set-ItemProperty -Path $GameDVRPath -Name "HistoricalCaptureEnabled" -Value 1 -Type DWord -Force
    }

    # 2. Chaves da GameBar (HKCU)
    $GameBarPath = "HKCU:\Software\Microsoft\GameBar"
    if (Test-Path $GameBarPath) {
        Set-ItemProperty -Path $GameBarPath -Name "UseNexusForGameBarEnabled" -Value 1 -Type DWord -Force
        Set-ItemProperty -Path $GameBarPath -Name "GameDVR_Enabled" -Value 1 -Type DWord -Force
    }

    # 3. Chave do GameConfigStore (HKCU)
    $GameStorePath = "HKCU:\System\GameConfigStore"
    if (Test-Path $GameStorePath) {
        Set-ItemProperty -Path $GameStorePath -Name "GameDVR_Enabled" -Value 1 -Type DWord -Force
    }

    # 4. Politicas de Grupo - GPO (HKLM)
    $GpoPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR"
    if (Test-Path $GpoPath) {
        Set-ItemProperty -Path $GpoPath -Name "AllowGameDVR" -Value 1 -Type DWord -Force
    }

    # 5. PolicyManager (HKLM)
    $PolicyPath = "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR"
    if (Test-Path $PolicyPath) {
        Set-ItemProperty -Path $PolicyPath -Name "value" -Value 1 -Type DWord -Force
    }

    Write-Output "[OK] Game DVR e gravacao de clipes reativados com sucesso!"
}
