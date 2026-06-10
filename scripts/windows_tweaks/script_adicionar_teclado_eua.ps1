param([string]$Acao = "Ativar")

Write-Host "Buscando lista de idiomas do usuario..." -ForegroundColor Yellow

$List = Get-WinUserLanguageList

if ($Acao -eq "Ativar") {
    Write-Host "Adicionando o idioma Ingles (Estados Unidos) com layout Estados Unidos (Internacional)..." -ForegroundColor Yellow
    
    # Adiciona en-US se nao estiver na lista
    if (-not ($List | Where-Object { $_.LanguageTag -eq 'en-US' })) {
        $List.Add("en-US")
    }
    
    # Configura o layout para Estados Unidos (Internacional)
    $EnUS = $List | Where-Object { $_.LanguageTag -eq 'en-US' }
    if ($EnUS) {
        $EnUS.InputMethodTips.Clear()
        $EnUS.InputMethodTips.Add("0409:00020409")
    }
    
    # Aplica as alteracoes de idioma e layout
    Set-WinUserLanguageList -LanguageList $List -Force
    Write-Host "Concluido! Idioma Ingles (Estados Unidos) com layout EUA Internacional adicionado com sucesso." -ForegroundColor Green
} else {
    Write-Host "Removendo o idioma Ingles (Estados Unidos)..." -ForegroundColor Yellow
    
    # Filtra para remover o idioma en-US
    $NewList = $List | Where-Object { $_.LanguageTag -ne 'en-US' }
    
    # Garante que a lista nao fique vazia
    if ($null -eq $NewList -or $NewList.Count -eq 0) {
        $NewList = New-WinUserLanguageList -Language "pt-BR"
    }
    
    Set-WinUserLanguageList -LanguageList $NewList -Force
    Write-Host "Concluido! Idioma Ingles (Estados Unidos) removido." -ForegroundColor Green
}
