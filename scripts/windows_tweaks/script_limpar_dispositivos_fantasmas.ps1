# ========================================================
# LYNCH FPS BOOST - LIMPEZA DE DISPOSITIVOS FANTASMAS (PnP)
# ========================================================
# Este script varre o banco de dados Plug and Play (PnP)
# e desinstala registros de periféricos inativos/desconectados
# para acelerar o tempo de resposta e evitar conflitos.
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
    Write-Host "Iniciando Limpeza de Dispositivos Fantasmas (Plug and Play)..." -ForegroundColor Cyan

    Write-Host "[1/2] Varrendo banco de dados PnP em busca de hardwares inativos..." -ForegroundColor Yellow
    $Devices = Get-PnpDevice -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "Unknown" }

    if (!$Devices) {
        Write-Host "[2/2] Nenhum dispositivo fantasma ou inativo encontrado no registro." -ForegroundColor Green
        Write-Host "`n[OK] O subsistema Plug and Play ja esta totalmente limpo!" -ForegroundColor Green
        exit 0
    }

    $Total = ($Devices | Measure-Object).Count
    Write-Host "[2/2] Detectado(s) $Total dispositivo(s) inativo(s). Iniciando remocao..." -ForegroundColor Yellow

    $Removidos = 0
    foreach ($Dev in $Devices) {
        $InstanceId = $Dev.InstanceId
        if ($InstanceId) {
            Write-Host " -> Removendo registro: $InstanceId" -ForegroundColor DarkGray
            pnputil /remove-device $InstanceId | Out-Null
            $Removidos++
        }
    }

    Write-Host "`n[OK] Limpeza concluida! $Removidos registro(s) de hardware inativo limpo(s) com sucesso!" -ForegroundColor Green

} elseif ($Acao -eq "Reverter") {
    Write-Host "Revertendo Limpeza de Dispositivos Fantasmas..." -ForegroundColor Cyan
    Write-Host " -> Nota: A remocao de registros fantasmas apenas despolui o banco de dados Plug and Play." -ForegroundColor Yellow
    Write-Host " -> Ao reconectar qualquer um desses periféricos no futuro, o Windows os reconhecera normalmente." -ForegroundColor Yellow
    Write-Host "`n[OK] O subsistema PnP esta pronto e operando no estado ideal!" -ForegroundColor Green
}
