param([string]$Acao = "Ativar")

if ($Acao -eq "Ativar") {
    Write-Host "Forcando o Windows a exibir extensoes de arquivos ocultas..."
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Value 0 -Force
    Write-Host "Concluido! Reinicie o computador para aplicar as mudancas."
} else {
    Write-Host "Ocultando extensoes de arquivos (Padrao)..."
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Value 1 -Force
    Write-Host "Concluido! Reinicie o computador para aplicar as mudancas."
}
