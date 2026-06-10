param([string]$Acao = "Ativar")

if ($Acao -eq "Ativar") {
    Write-Host "Acelerando Taxa de Repeticao do Teclado (Foco Gamer / Baixa Latencia)..."
    
    # 1. Configuracoes padrao do teclado (atraso minimo e velocidade maxima)
    Set-ItemProperty -Path "HKCU:\Control Panel\Keyboard" -Name "KeyboardDelay" -Value "0" -Force
    Set-ItemProperty -Path "HKCU:\Control Panel\Keyboard" -Name "KeyboardSpeed" -Value "31" -Force

    # 2. Ajustes de Acessibilidade avancados (Keyboard Response para menor delay)
    $KeyboardResponsePath = "HKCU:\Control Panel\Accessibility\Keyboard Response"
    if (-not (Test-Path -Path $KeyboardResponsePath)) {
        New-Item -Path $KeyboardResponsePath -Force | Out-Null
    }
    Set-ItemProperty -Path $KeyboardResponsePath -Name "AutoRepeatDelay" -Value "200" -Force
    Set-ItemProperty -Path $KeyboardResponsePath -Name "AutoRepeatRate" -Value "15" -Force
    Set-ItemProperty -Path $KeyboardResponsePath -Name "BounceTime" -Value "0" -Force
    Set-ItemProperty -Path $KeyboardResponsePath -Name "DelayBeforeAcceptance" -Value "0" -Force
    Set-ItemProperty -Path $KeyboardResponsePath -Name "Flags" -Value "59" -Force

    Write-Host "Concluido! Reinicie o computador para aplicar totalmente as mudancas."
} else {
    Write-Host "Restaurando Taxa de Repeticao do Teclado ao Padrao do Windows..."

    # 1. Restaurar valores padrao do teclado
    Set-ItemProperty -Path "HKCU:\Control Panel\Keyboard" -Name "KeyboardDelay" -Value "1" -Force
    Set-ItemProperty -Path "HKCU:\Control Panel\Keyboard" -Name "KeyboardSpeed" -Value "31" -Force

    # 2. Restaurar acessibilidade padrao (desativar custom overrides)
    $KeyboardResponsePath = "HKCU:\Control Panel\Accessibility\Keyboard Response"
    if (Test-Path -Path $KeyboardResponsePath) {
        Set-ItemProperty -Path $KeyboardResponsePath -Name "AutoRepeatDelay" -Value "1000" -Force
        Set-ItemProperty -Path $KeyboardResponsePath -Name "AutoRepeatRate" -Value "500" -Force
        Set-ItemProperty -Path $KeyboardResponsePath -Name "BounceTime" -Value "0" -Force
        Set-ItemProperty -Path $KeyboardResponsePath -Name "DelayBeforeAcceptance" -Value "1000" -Force
        Set-ItemProperty -Path $KeyboardResponsePath -Name "Flags" -Value "126" -Force
    }

    Write-Host "Concluido! Reinicie o computador para aplicar totalmente as mudancas."
}
