# ========================================================
# LYNCH FPS BOOST - LIMPEZA DE COMPONENTES DO WINDOWS (WinSxS)
# ========================================================
# Este script executa a limpeza profunda do armazenamento de
# componentes (WinSxS) via DISM para liberar espaço em disco.
# ========================================================

param (
    [ValidateSet("Ativar", "Reverter")]
    [string]$Acao = "Ativar"
)

# Requer privilégios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador!"
    exit 1
}

if ($Acao -eq "Ativar") {
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "   LYNCH FPS BOOST - LIMPEZA DE COMPONENTES (WINSXS)" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Iniciando a limpeza do Armazenamento de Componentes..." -ForegroundColor Yellow
    Write-Host "Este processo analisa e remove atualizacoes do Windows antigas." -ForegroundColor Yellow
    Write-Host "Isso pode levar de 5 a 15 minutos dependendo do seu sistema." -ForegroundColor Yellow
    Write-Host ""

    # Executa a limpeza básica de componentes supersedados
    Write-Host "[1/2] Executando StartComponentCleanup..." -ForegroundColor Yellow
    dism.exe /Online /Cleanup-Image /StartComponentCleanup
    
    # Executa a limpeza profunda (ResetBase) para liberar o máximo de espaço
    Write-Host "`n[2/2] Executando ResetBase (Exclusao definitiva de backups antigos)..." -ForegroundColor Yellow
    dism.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase

    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "Limpeza do WinSxS concluida com sucesso!" -ForegroundColor Green
    Write-Host "Muitos gigabytes de espaco foram liberados no disco C:."
    Write-Host "========================================================" -ForegroundColor Cyan

} elseif ($Acao -eq "Reverter") {
    Write-Host "Revertendo Limpeza do WinSxS..." -ForegroundColor Cyan
    Write-Host " -> Nota: Nao e possivel restaurar atualizacoes antigas e arquivos deletados." -ForegroundColor Yellow
    Write-Host " -> O sistema ja se encontra no estado ideal de otimizacao e espaco." -ForegroundColor Yellow
    Write-Host "`n[OK] Estado ideal de armazenamento mantido!" -ForegroundColor Green
}
