# Requer privilegios de administrador
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Este script precisa ser executado como Administrador!"
    exit
}

Write-Host "Varrendo o Security Center para obter o status do Antivirus..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------"

try {
    $avProducts = Get-CimInstance -Namespace "root\SecurityCenter2" -ClassName "AntiVirusProduct" -ErrorAction Stop

    if ($null -eq $avProducts -or $avProducts.Count -eq 0) {
        Write-Host "Nenhum antivirus de terceiros detectado no Security Center." -ForegroundColor Yellow
        # Verifica se o Windows Defender Service está rodando
        $defenderService = Get-Service -Name "Windefend" -ErrorAction SilentlyContinue
        if ($defenderService) {
            $status = if ($defenderService.Status -eq "Running") { "Ativo (Servico em Execucao)" } else { "Inativo" }
            $color = if ($defenderService.Status -eq "Running") { "Green" } else { "Red" }
            Write-Host "Antivirus Padrao: Windows Defender" -ForegroundColor Cyan
            Write-Host "• Status do Servico: $status" -ForegroundColor $color
        } else {
            Write-Host "Nenhum antivirus ou servico do Windows Defender pode ser localizado." -ForegroundColor Red
        }
    } else {
        Write-Host "Encontrado(s) $($avProducts.Count) produto(s) antivirus:`n" -ForegroundColor Yellow
        foreach ($av in $avProducts) {
            $name = $av.displayName
            $state = $av.productState
            
            # Converte o estado para hexadecimal de 6 caracteres
            $stateHex = "{0:x6}" -f $state
            
            # Proteção em Tempo Real: bit 12 (0x1000) ativo ou segundo byte iniciando com 1
            $realTimeActive = ($state -band 0x1000) -ne 0 -or $stateHex.Substring(2, 1) -eq "1"
            
            # Definições/Assinaturas: bit 4 (0x0010) indica desatualizado
            $signaturesUpToDate = ($state -band 0x0010) -eq 0
            
            $rtStatus = if ($realTimeActive) { "ATIVADA" } else { "DESATIVADA" }
            $rtColor = if ($realTimeActive) { "Green" } else { "Red" }
            
            $sigStatus = if ($signaturesUpToDate) { "Atualizadas" } else { "Desatualizadas" }
            $sigColor = if ($signaturesUpToDate) { "Green" } else { "Yellow" }
            
            Write-Host "Antivirus: $name" -ForegroundColor Cyan
            Write-Host "• Protecao em Tempo Real: $rtStatus" -ForegroundColor $rtColor
            Write-Host "• Assinaturas de Virus: $sigStatus" -ForegroundColor $sigColor
            Write-Host "• Codigo do Estado WMI: 0x$stateHex ($state)" -ForegroundColor Gray
            Write-Host "--------------------------------------------------------"
        }
    }
} catch {
    # Em sistemas Windows Server, a classe SecurityCenter2 não existe por padrão
    Write-Warning "Nao foi possivel consultar a classe WMI SecurityCenter2: $_"
    Write-Host "`nConsultando servico nativo do Windows Defender..." -ForegroundColor Yellow
    
    $defenderService = Get-Service -Name "Windefend" -ErrorAction SilentlyContinue
    if ($defenderService) {
        $status = if ($defenderService.Status -eq "Running") { "Ativo (Servico em Execucao)" } else { "Inativo" }
        $color = if ($defenderService.Status -eq "Running") { "Green" } else { "Red" }
        Write-Host "Antivirus: Windows Defender (Windows Server)" -ForegroundColor Cyan
        Write-Host "• Status do Servico (Windefend): $status" -ForegroundColor $color
    } else {
        Write-Host "O servico Windows Defender nao esta instalado ou disponivel." -ForegroundColor Red
    }
}
