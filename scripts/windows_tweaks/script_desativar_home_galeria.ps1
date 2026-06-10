param([string]$Acao = "Ativar")

# Requer privilegios de administrador
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Este script precisa ser executado como Administrador!"
    exit
}

$HomeKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{e88865ea-0e1c-4e20-9aa6-edcd0212c87c}"
$GalleryKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{f874310e-b6b7-47dc-bc84-b9e6b38f5903}"

if ($Acao -eq "Ativar") {
    Write-Host "Desativando as secoes Inicio e Galeria do Explorador de Arquivos..." -ForegroundColor Yellow
    
    if (Test-Path $HomeKey) {
        Remove-Item -Path $HomeKey -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $GalleryKey) {
        Remove-Item -Path $GalleryKey -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer" -Name "ShowRecent" -Value 0 -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer" -Name "ShowFrequent" -Value 0 -ErrorAction SilentlyContinue
    Stop-Service -Name "TrkWks" -Force -ErrorAction SilentlyContinue
    Set-Service -Name "TrkWks" -StartupType Disabled -ErrorAction SilentlyContinue
    
    Write-Host "Concluido! Secoes Inicio, Galeria e rastreamento de arquivos desativados." -ForegroundColor Green
} else {
    Write-Host "Restaurando as secoes Inicio e Galeria do Explorador de Arquivos..." -ForegroundColor Yellow
    
    if (!(Test-Path $HomeKey)) {
        $null = New-Item -Path $HomeKey -Value "{e88865ea-0e1c-4e20-9aa6-edcd0212c87c}" -Force -ErrorAction SilentlyContinue
    }
    if (!(Test-Path $GalleryKey)) {
        $null = New-Item -Path $GalleryKey -Value "CLSID_MSGraphHomeFolder" -Force -ErrorAction SilentlyContinue
    }
    
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer" -Name "ShowRecent" -Value 1 -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer" -Name "ShowFrequent" -Value 1 -ErrorAction SilentlyContinue
    Set-Service -Name "TrkWks" -StartupType Automatic -ErrorAction SilentlyContinue
    Start-Service -Name "TrkWks" -ErrorAction SilentlyContinue
    
    Write-Host "Concluido! Secoes Inicio, Galeria e rastreamento restaurados." -ForegroundColor Green
}
