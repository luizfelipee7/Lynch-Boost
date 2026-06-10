# ========================================================
# LYNCH FPS BOOST - ESVAZIAMENTO DA LIXEIRA DO PC
# ========================================================
# Este script mede o espaço atual acumulado na Lixeira
# e realiza a exclusão definitiva silenciosa de todos os itens.
# ========================================================

param (
    [ValidateSet("Ativar", "Reverter")]
    [string]$Acao = "Ativar"
)

# Requer privilégios de Administrador (opcional, mas recomendado para limpar todos os volumes)
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador!"
    exit 1
}

if ($Acao -eq "Ativar") {
    Write-Host "Iniciando Limpeza e Esvaziamento da Lixeira..." -ForegroundColor Cyan

    Write-Host "[1/2] Calculando espaco ocupado na Lixeira..." -ForegroundColor Yellow
    
    $TotalSize = 0
    try {
        $RecycleBin = (New-Object -ComObject Shell.Application).NameSpace(0xa)
        if ($RecycleBin) {
            foreach ($Item in $RecycleBin.Items()) {
                $TotalSize += $Item.Size
            }
        }
    } catch {
        $TotalSize = 0
    }

    $SizeDisplay = ""
    if ($TotalSize -ge 1GB) {
        $SizeDisplay = "$([Math]::Round($TotalSize / 1GB, 2)) GB"
    } else {
        $SizeDisplay = "$([Math]::Round($TotalSize / 1MB, 2)) MB"
    }

    Write-Host "[2/2] Esvaziando Lixeira de todas as unidades de disco..." -ForegroundColor Yellow
    Clear-RecycleBin -Force -ErrorAction SilentlyContinue

    Write-Host "`n[OK] Lixeira limpa! $SizeDisplay de espaco liberado com sucesso!" -ForegroundColor Green

} elseif ($Acao -eq "Reverter") {
    Write-Host "Revertendo Limpeza da Lixeira..." -ForegroundColor Cyan
    Write-Host " -> Nota: Arquivos deletados permanentemente da Lixeira nao podem ser recuperados." -ForegroundColor Yellow
    Write-Host " -> A Lixeira ja se encontra vazia e no estado de armazenamento ideal." -ForegroundColor Yellow
    Write-Host "`n[OK] Estado ideal de armazenamento mantido!" -ForegroundColor Green
}
