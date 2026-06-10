# Requer privilegios de administrador
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Este script precisa ser executado como Administrador!"
    exit
}

Write-Host "Buscando registros de Tela Azul (BSOD) no sistema..."
Write-Host "--------------------------------------------------------"

$query = @"
<QueryList>
<Query Id="0" Path="System">
<Select Path="System">*[System[Provider[@Name='Microsoft-Windows-WER-SystemErrorReporting'] and (EventID=1001)]]</Select>
</Query>
</QueryList>
"@

try {
    $bsodEvents = Get-WinEvent -FilterXml $query -ErrorAction Stop
    
    if ($bsodEvents.Count -eq 0) {
        Write-Host "Nenhum evento de Tela Azul (BSOD) encontrado." -ForegroundColor Green
    } else {
        Write-Host "Encontrado(s) $($bsodEvents.Count) evento(s) de BSOD recente(s):`n" -ForegroundColor Yellow
        foreach ($event in $bsodEvents) {
            $eventData = [xml]$event.ToXml()
            $eventDetails = $eventData.Event.EventData.Data
            
            Write-Host "Data/Hora: $($event.TimeCreated)"
            if ($eventDetails -and $eventDetails.Count -ge 6) {
                Write-Host "Codigo de Verificacao (BugCheck): $($eventDetails[0].'#text')"
                Write-Host "Parametro 1: $($eventDetails[1].'#text')"
                Write-Host "Parametro 2: $($eventDetails[2].'#text')"
                Write-Host "Parametro 3: $($eventDetails[3].'#text')"
                Write-Host "Parametro 4: $($eventDetails[4].'#text')"
                Write-Host "Arquivo de Despejo (Dump): $($eventDetails[5].'#text')"
            } else {
                Write-Host "Descricao: $($event.Message)"
            }
            Write-Host "--------------------------------------------------------"
        }
    }
} catch {
    # Se nao houver eventos correspondentes, o Get-WinEvent gera excecao
    if ($_.Exception.Message -like "*No events*" -or $_.Exception.Message -like "*encontrado*" -or $_.Exception.Message -like "*correspondente*") {
        Write-Host "Nenhum registro de Tela Azul (BSOD) encontrado no sistema." -ForegroundColor Green
    } else {
        Write-Warning "Nao foi possivel consultar os logs do sistema: $_"
    }
}
