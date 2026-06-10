param([string]$Acao = "Ativar")

$RegistryPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel"
$IconKey = "{B2B4A4D1-2754-4140-A2EB-9A76D9D7CDC6}"

if ($Acao -eq "Ativar") {
    Write-Host "Ocultando o icone do Linux WSL no Meu Computador..." -ForegroundColor Yellow
    
    if (!(Test-Path $RegistryPath)) {
        $null = New-Item -Path $RegistryPath -Force -ErrorAction SilentlyContinue
    }
    
    Set-ItemProperty -Path $RegistryPath -Name $IconKey -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    
    Write-Host "Concluido! Icone do Linux WSL ocultado." -ForegroundColor Green
} else {
    Write-Host "Restaurando o icone do Linux WSL no Meu Computador..." -ForegroundColor Yellow
    
    if (Test-Path $RegistryPath) {
        Remove-ItemProperty -Path $RegistryPath -Name $IconKey -ErrorAction SilentlyContinue
    }
    
    Write-Host "Concluido! Icone do Linux WSL restaurado." -ForegroundColor Green
}
