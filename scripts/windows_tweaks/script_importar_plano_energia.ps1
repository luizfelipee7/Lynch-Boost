Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   LYNCH FPS BOOST - MOTOR DE ENERGIA" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Pega a pasta onde este script está rodando e procura o novo arquivo
$PowPath = Join-Path -Path $PSScriptRoot -ChildPath "plano_lynch.pow"

if (-Not (Test-Path $PowPath)) {
    Write-Host "[ERRO] Arquivo .pow nao encontrado em: $PowPath" -ForegroundColor Red
    Start-Sleep 5
    exit
}

Write-Host "`nImportando o perfil de energia Lynch..." -ForegroundColor Yellow
$resultado = powercfg -import "`"$PowPath`""

# Expressao Regular (Regex) para encontrar o codigo GUID gerado pelo Windows
$guid = [regex]::Match($resultado, '([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})').Value

if ($guid) {
    Write-Host "[SUCESSO] Plano importado com o ID: $guid" -ForegroundColor Green
    Write-Host "Ativando o plano de maxima performance e Core Unparking..." -ForegroundColor Yellow
    powercfg -setactive $guid
    Write-Host "Renomeando o plano para o padrao Lynch..." -ForegroundColor Yellow
    powercfg -changename SCHEME_CURRENT "Lynch FPS Boost (Desempenho Extremo)" "Otimizado para menor Input Lag e maximo FPS."
    Write-Host "Configurando para nunca desligar o video e nunca suspender..." -ForegroundColor Yellow
    powercfg /change monitor-timeout-ac 0
    powercfg /change monitor-timeout-dc 0
    powercfg /change standby-timeout-ac 0
    powercfg /change standby-timeout-dc 0
    Write-Host "`nO Plano LYNCH FPS BOOST foi ativado e travado no sistema!" -ForegroundColor Cyan
} else {
    Write-Host "`n[ERRO] Falha ao extrair o identificador do plano." -ForegroundColor Red
}

Start-Sleep 4