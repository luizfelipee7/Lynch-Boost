# Requer privilegios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Output "Iniciando otimizacoes agressivas para reducao de Input Lag..."

# 1. BCDEDIT Tweaks (Temporizadores & Latência de Interrupção)
Write-Output "Aplicando configuracoes de temporizador e clock de baixa latência (BCDEDIT)..."
# Ignora erros se a chave nao existir antes de tentar deletar
bcdedit /deletevalue useplatformclock 2>$null | Out-Null
bcdedit /set disabledynamictick yes 2>$null | Out-Null
bcdedit /set useplatformtick yes 2>$null | Out-Null
bcdedit /set x2apicpolicy Enable 2>$null | Out-Null
bcdedit /set usephysicaldestination No 2>$null | Out-Null
bcdedit /set tscsyncpolicy Enhanced 2>$null | Out-Null

# 2. Desativação física do HPET (High Precision Event Timer) via PnP/WMIC
Write-Output "Desativando o dispositivo High Precision Event Timer (HPET) no Gerenciador de Dispositivos..."
try {
    $HpetDevice = Get-PnpDevice -FriendlyName "High precision event timer" -ErrorAction SilentlyContinue
    if ($HpetDevice) {
        # Se o dispositivo existir e estiver ativo (Status "OK"), tentamos desabilitar
        if ($HpetDevice.Status -eq "OK") {
            $HpetDevice | Disable-PnpDevice -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
        }
    } else {
        # Fallback para wmic somente se o executável estiver disponível no sistema
        if (Get-Command "wmic" -ErrorAction SilentlyContinue) {
            wmic path Win32_PnPEntity where "name='High precision event timer'" call disable 2>$null | Out-Null
        }
    }
} catch {
    # Silencia qualquer erro inesperado
}

# 2. Forcar Tela Cheia Exclusiva e Desativar GameDVR (DWM Bypass)
Write-Output "Desativando otimizacoes de tela cheia globalmente e GameDVR..."
$GameConfigStore = "HKCU:\System\GameConfigStore"
if (Test-Path $GameConfigStore) {
    Set-ItemProperty -Path $GameConfigStore -Name "GameDVR_FSEBehaviorMode" -Value 2 -Type DWord -Force
    Set-ItemProperty -Path $GameConfigStore -Name "GameDVR_HonorUserFSEBehaviorMode" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $GameConfigStore -Name "GameDVR_FSEBehavior" -Value 2 -Type DWord -Force
    Set-ItemProperty -Path $GameConfigStore -Name "GameDVR_DXGIHonorFSEWindowsCompatible" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $GameConfigStore -Name "GameDVR_Enabled" -Value 0 -Type DWord -Force
}

$AllowGameDVR = "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR"
if (Test-Path $AllowGameDVR) {
    Set-ItemProperty -Path $AllowGameDVR -Name "value" -Value 0 -Type DWord -Force
}

# 3. Prioridade e Fila de Periféricos (Mouclass & Kbdclass)
Write-Output "Otimizando filas de dados do Mouse (Mouclass) e Teclado (Kbdclass) para latência mínima..."
$Mouclass = "HKLM:\SYSTEM\CurrentControlSet\Services\mouclass\Parameters"
if (Test-Path $Mouclass) {
    # Reduzir de 100/200 para 16 (Limite máximo de responsividade estável para mouses de alta polling rate)
    Set-ItemProperty -Path $Mouclass -Name "MouseDataQueueSize" -Value 16 -Type DWord -Force
}

$Kbdclass = "HKLM:\SYSTEM\CurrentControlSet\Services\kbdclass\Parameters"
if (Test-Path $Kbdclass) {
    # Reduzir para 16 (0x10) para tempo de resposta do teclado ultra-rapido
    Set-ItemProperty -Path $Kbdclass -Name "KeyboardDataQueueSize" -Value 16 -Type DWord -Force
}

# 4. Desativar Aceleração do Mouse e Forçar Paridade 1:1 Pixel
Write-Output "Removendo aceleracao de mouse e ativando movimentos de paridade 1:1..."
$MousePath = "HKCU:\Control Panel\Mouse"
if (Test-Path $MousePath) {
    Set-ItemProperty -Path $MousePath -Name "MouseSpeed" -Value "0" -Type String -Force
    Set-ItemProperty -Path $MousePath -Name "MouseThreshold1" -Value "0" -Type String -Force
    Set-ItemProperty -Path $MousePath -Name "MouseThreshold2" -Value "0" -Type String -Force
    Set-ItemProperty -Path $MousePath -Name "MouseSensitivity" -Value "10" -Type String -Force
}

# 5. Otimizar Responsividade do Teclado (Delay e Speed de Repetição)
Write-Output "Minimizando atraso e maximizando a taxa de repetição do Teclado..."
$KeyboardPath = "HKCU:\Control Panel\Keyboard"
if (Test-Path $KeyboardPath) {
    Set-ItemProperty -Path $KeyboardPath -Name "KeyboardDelay" -Value "0" -Type String -Force
    Set-ItemProperty -Path $KeyboardPath -Name "KeyboardSpeed" -Value "31" -Type String -Force
}

# 6. Desativar Teclas de Acessibilidade Irritantes (Sticky, Toggle, Filter e Mouse Keys)
Write-Output "Extirpando atalhos de acessibilidade indesejados..."
$KeyboardResponse = "HKCU:\Control Panel\Accessibility\Keyboard Response"
if (Test-Path $KeyboardResponse) { Set-ItemProperty -Path $KeyboardResponse -Name "Flags" -Value "122" -Type String -Force }

$ToggleKeys = "HKCU:\Control Panel\Accessibility\ToggleKeys"
if (Test-Path $ToggleKeys) { Set-ItemProperty -Path $ToggleKeys -Name "Flags" -Value "58" -Type String -Force }

$StickyKeys = "HKCU:\Control Panel\Accessibility\StickyKeys"
if (Test-Path $StickyKeys) { Set-ItemProperty -Path $StickyKeys -Name "Flags" -Value "506" -Type String -Force }

$MouseKeys = "HKCU:\Control Panel\Accessibility\MouseKeys"
if (Test-Path $MouseKeys) { Set-ItemProperty -Path $MouseKeys -Name "Flags" -Value "0" -Type String -Force }

# 7. Elevar o processador de inputs CSRSS do Windows para Tempo Real
Write-Output "Elevando a prioridade do subsistema de inputs do Windows (CSRSS) para Tempo Real..."
$CsrssPerf = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\csrss.exe\PerfOptions"
if (!(Test-Path $CsrssPerf)) { New-Item -Path $CsrssPerf -Force | Out-Null }
Set-ItemProperty -Path $CsrssPerf -Name "CpuPriorityClass" -Value 4 -Type DWord -Force
Set-ItemProperty -Path $CsrssPerf -Name "IoPriority" -Value 3 -Type DWord -Force

# 8. Otimizar Quantum do CPU (Win32PrioritySeparation = 38 / 0x26)
Write-Output "Ajustando o Quantum de alocacao da CPU (Win32PrioritySeparation)..."
$PriorityPath = "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl"
if (Test-Path $PriorityPath) {
    Set-ItemProperty -Path $PriorityPath -Name "Win32PrioritySeparation" -Value 38 -Type DWord -Force -ErrorAction SilentlyContinue
}

Write-Output "Otimizacoes agressivas de Input Lag concluidas com sucesso!"
