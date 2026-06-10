$GameBarPath = "HKCU:\SOFTWARE\Microsoft\GameBar"

Write-Host "Ativando o Game Mode do Windows..." -ForegroundColor Yellow

# Ativar Game Mode (EXM)
if (!(Test-Path $GameBarPath)) {
    New-Item -Path $GameBarPath -Force | Out-Null
}
Set-ItemProperty -Path $GameBarPath -Name "AllowAutoGameMode" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $GameBarPath -Name "AutoGameModeEnabled" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue

Write-Host "Concluido! O Game Mode foi ativado com sucesso." -ForegroundColor Green
