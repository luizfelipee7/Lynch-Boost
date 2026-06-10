param([string]$Acao = "Ativar")

Write-Host "Buscando lista de idiomas do usuario..." -ForegroundColor Yellow

$List = Get-WinUserLanguageList
$PtBr = $List | Where-Object { $_.LanguageTag -eq 'pt-BR' }

if ($null -eq $PtBr) {
    Write-Warning "Idioma Portugues (Brasil) nao encontrado na lista de idiomas do usuario."
    exit
}

if ($Acao -eq "Ativar") {
    Write-Host "Forcando apenas layout ABNT2 para Portugues (Brasil)..." -ForegroundColor Yellow
    
    # Limpa e adiciona somente ABNT2 (0416:00010416)
    $PtBr.InputMethodTips.Clear()
    $PtBr.InputMethodTips.Add('0416:00010416')
    
    Set-WinUserLanguageList -LanguageList $List -Force
    Write-Host "Concluido! Layout ABNT (ABNT1) removido. Apenas ABNT2 mantido ativo." -ForegroundColor Green
} else {
    Write-Host "Restaurando layout ABNT (ABNT1) secundario..." -ForegroundColor Yellow
    
    # Re-adiciona ABNT1 (0416:00000416) se nao estiver presente
    if ($PtBr.InputMethodTips -notcontains '0416:00000416') {
        $PtBr.InputMethodTips.Add('0416:00000416')
    }
    
    Set-WinUserLanguageList -LanguageList $List -Force
    Write-Host "Concluido! Layout ABNT (ABNT1) restaurado com sucesso." -ForegroundColor Green
}
