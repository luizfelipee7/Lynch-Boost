param([string]$Acao = "Ativar")

$PolicyPath1 = "HKLM:\SOFTWARE\Microsoft\PolicyManager\current\device\System"
$PolicyPath2 = "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\System\AllowExperimentation"
$PolicyPath3 = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PreviewBuilds"

if ($Acao -eq "Ativar") {
    Write-Host "Desativando Experimentos e Recursos de Testes do Windows..." -ForegroundColor Yellow
    
    if (!(Test-Path $PolicyPath1)) {
        New-Item -Path $PolicyPath1 -Force | Out-Null
    }
    Set-ItemProperty -Path $PolicyPath1 -Name "AllowExperimentation" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    if (!(Test-Path $PolicyPath2)) {
        New-Item -Path $PolicyPath2 -Force | Out-Null
    }
    Set-ItemProperty -Path $PolicyPath2 -Name "value" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    if (!(Test-Path $PolicyPath3)) {
        New-Item -Path $PolicyPath3 -Force | Out-Null
    }
    Set-ItemProperty -Path $PolicyPath3 -Name "AllowBuildPreview" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    Write-Host "Concluido! Os experimentos e testes do Windows Insider foram desativados." -ForegroundColor Green
} else {
    Write-Host "Reativando Experimentos e Recursos de Testes do Windows..." -ForegroundColor Yellow
    
    if (Test-Path $PolicyPath1) {
        Remove-ItemProperty -Path $PolicyPath1 -Name "AllowExperimentation" -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $PolicyPath2) {
        Remove-ItemProperty -Path $PolicyPath2 -Name "value" -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $PolicyPath3) {
        Remove-ItemProperty -Path $PolicyPath3 -Name "AllowBuildPreview" -Force -ErrorAction SilentlyContinue
    }

    Write-Host "Concluido! Os experimentos e testes do Windows Insider foram reativados." -ForegroundColor Green
}
