param([string]$Acao = "Ativar")

if ($Acao -eq "Ativar") {
    Write-Host "Desativando Teclas de Aderencia (Foco Gamer)..."
    Set-ItemProperty -Path "HKCU:\Control Panel\Accessibility\StickyKeys" -Name "Flags" -Value "506" -Force
    Write-Host "Concluido! Reinicie o computador para aplicar as mudancas."
} else {
    Write-Host "Ativando Teclas de Aderencia (Padrao do Windows)..."
    Set-ItemProperty -Path "HKCU:\Control Panel\Accessibility\StickyKeys" -Name "Flags" -Value "510" -Force
    Write-Host "Concluido! Reinicie o computador para aplicar as mudancas."
}
