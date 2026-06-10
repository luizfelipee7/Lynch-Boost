param (
    [ValidateSet("Ativar", "Reverter")]
    [string]$Acao = "Ativar"
)

# Requer privilégios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador!"
    exit 1
}

$RegPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"

if ($Acao -eq "Ativar") {
    Write-Host "Ativando Otimizacoes Globais de GPU..." -ForegroundColor Cyan
    try {
        # 1. Forçar alocação contígua de buffers de vídeo no IOMMU
        Write-Host "Forcando alocacao de buffers contigos no IOMMU..." -ForegroundColor Yellow
        if (!(Test-Path $RegPath)) { New-Item -Path $RegPath -Force | Out-Null }
        Set-ItemProperty -Path $RegPath -Name "DpiMapIommuContiguous" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
        
        Write-Host "[OK] Otimizacoes globais de GPU aplicadas com sucesso!" -ForegroundColor Green
        Write-Host "Reinicie o computador para aplicar as alteracoes no kernel grafico." -ForegroundColor Yellow
    } catch {
        Write-Error "Falha ao aplicar alteracao no Registro: $_"
        exit 1
    }
} else {
    Write-Host "Revertendo Otimizacoes Globais de GPU..." -ForegroundColor Cyan
    try {
        # 1. Remover alocação contígua do IOMMU
        Write-Host "Removendo alocacao de buffers contigos no IOMMU..." -ForegroundColor Yellow
        if (Test-Path $RegPath) {
            Remove-ItemProperty -Path $RegPath -Name "DpiMapIommuContiguous" -ErrorAction SilentlyContinue
        }
        
        Write-Host "[OK] Otimizacoes globais de GPU removidas (restauradas ao padrao)!" -ForegroundColor Green
        Write-Host "Reinicie o computador para reverter as alteracoes no kernel grafico." -ForegroundColor Yellow
    } catch {
        Write-Error "Falha ao remover alteracao no Registro: $_"
        exit 1
    }
}
exit 0
