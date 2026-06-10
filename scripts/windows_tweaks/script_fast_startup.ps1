param([string]$Acao = "Ativar")

if ($Acao -eq "Ativar") {
    Write-Host "Desativando Inicializacao Rapida (Fast Startup) para evitar bugs..."
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name "HiberbootEnabled" -Value 0 -Force
    Write-Host "Concluido! Reinicie o computador para aplicar as mudancas."
} else {
    Write-Host "Ativando Inicializacao Rapida (Fast Startup) - Padrao do Windows..."
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name "HiberbootEnabled" -Value 1 -Force
    Write-Host "Concluido! Reinicie o computador para aplicar as mudancas."
}
