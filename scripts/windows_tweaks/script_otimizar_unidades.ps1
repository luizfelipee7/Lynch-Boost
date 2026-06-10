# Requer privilegios de Administrador para garantir acesso a otimizacao de disco
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Output "========================================================"
Write-Output "   OTIMIZADOR INTELIGENTE DE ARMAZENAMENTO (TRIM & DEFRAG)   "
Write-Output "========================================================"
Write-Output ""

# Aplicar otimizações adicionais de comportamento do sistema de arquivos NTFS (EXM)
try {
    Write-Output "[*] Aplicando otimizações avançadas de comportamento NTFS..."
    fsutil behavior set mftzone 4 | Out-Null
    fsutil behavior set disablelastaccess 1 | Out-Null
    fsutil behavior set encryptpagingfile 0 | Out-Null
    fsutil behavior set disabledeletenotify 0 | Out-Null
    Write-Output "[OK] Comportamento NTFS otimizado (desativados acessos de data, pagefile criptografia e ativado TRIM)!"
}
catch {
    Write-Output "[!] Falha ao configurar políticas NTFS avancadas: $_"
}
Write-Output ""

# Buscar todos os volumes locais que sao discos fixos, ignorando pendrives,
# particoes de recuperação ocultas e discos na nuvem/virtuais (como o Google Drive).
$Volumes = Get-Volume | Where-Object {
    $_.DriveType -eq 'Fixed' -and
    $_.DriveLetter -ne $null -and
    $_.FileSystemLabel -notlike "*Google Drive*" -and
    $_.FileSystemType -ne "GoogleDriveFS" -and
    $_.FileSystemType -ne "Virtual"
}

if ($Volumes.Count -eq 0) {
    Write-Output "[!] Nenhuma unidade local compativel com otimizacao foi encontrada."
    exit
}

Write-Output "[*] Detectando unidades locais para otimizacao segura..."
foreach ($Vol in $Volumes) {
    $Letra = $Vol.DriveLetter
    $Label = $Vol.FileSystemLabel
    if ([string]::IsNullOrEmpty($Label)) { $Label = "Sem Nome" }
    
    Write-Output "--------------------------------------------------------"
    Write-Output "Unidade encontrada: [$($Letra):] ($Label) - Tipo: $($Vol.FileSystemType)"
    
    $MediaType = "Desconhecido"
    try {
        # Obter informacoes fisicas da unidade de forma isolada e segura
        $Partition = Get-Partition -DriveLetter $Letra -ErrorAction Stop
        if ($Partition) {
            # Pega a primeira particao caso retorne multiplas particoes
            $DiskNumber = $Partition[0].DiskNumber
            $Disk = Get-PhysicalDisk | Where-Object { $_.DeviceID -eq $DiskNumber } -ErrorAction Stop
            if ($Disk) {
                $MediaType = $Disk.MediaType
            }
        }
    }
    catch {
        # Ignora silenciosamente erros de deteccao fisica para nao abortar a otimizacao
    }
    
    try {
        if ($MediaType -eq "SSD") {
            Write-Output "[+] Tipo de midia: SSD (Estado Solido)"
            Write-Output "[*] Enviando comando TRIM (ReTrim) para liberar blocos inativos..."
            # TRIM e extremamente rapido e mantem a performance do SSD intacta
            Optimize-Volume -DriveLetter $Letra -ReTrim -Verbose 2>&1 | ForEach-Object { Write-Output "   $_" }
            Write-Output "[OK] SSD ($($Letra):) otimizado com sucesso!"
        }
        elseif ($MediaType -eq "HDD") {
            Write-Output "[+] Tipo de midia: HDD (Disco Mecanico)"
            Write-Output "[*] Desfragmentando arquivos para otimizar leitura sequencial..."
            Optimize-Volume -DriveLetter $Letra -Defrag -Verbose 2>&1 | ForEach-Object { Write-Output "   $_" }
            Write-Output "[OK] HDD ($($Letra):) desfragmentado e otimizado com sucesso!"
        }
        else {
            # Se nao for possivel detectar a midia com precisao, executamos a otimizacao padrao do Windows
            Write-Output "[+] Tipo de midia: Nao especificado (Detectando automaticamente...)"
            Write-Output "[*] Executando otimizacao geral adequada..."
            Optimize-Volume -DriveLetter $Letra -Verbose 2>&1 | ForEach-Object { Write-Output "   $_" }
            Write-Output "[OK] Unidade ($($Letra):) otimizada com sucesso!"
        }
    }
    catch {
        Write-Output "[X] Erro ao otimizar a unidade $($Letra): $_"
    }
}

Write-Output "--------------------------------------------------------"
Write-Output "[OK] Otimizacao inteligente de armazenamento concluida!"
