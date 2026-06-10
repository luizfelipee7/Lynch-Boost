param([string]$Acao = "Ativar")

if ($Acao -eq "Ativar") {
    Write-Host "Forcando Explorador de Arquivos a abrir no 'Meu Computador'..."
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "LaunchTo" -Value 1 -Force
    Write-Host "Concluido! Reinicie o computador para aplicar as mudancas."
} else {
    Write-Host "Revertendo Explorador de Arquivos para o padrao (Inicio)..."
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "LaunchTo" -Value 2 -Force
    Write-Host "Concluido! Reinicie o computador para aplicar as mudancas."
}
