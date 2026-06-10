# ========================================================
# LYNCH FPS BOOST - OTIMIZAÇÃO DE MEMÓRIA RAM & PAGEFILE
# ========================================================
# Este script otimiza a alocação física da memória RAM.
# Ele desativa a compressão de RAM em sistemas com >= 16GB,
# força o kernel e drivers a residirem estritamente na RAM,
# e reagrupa os processos svchost.exe para liberar memória.
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

$RegistryMemory = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"

if ($Acao -eq "Ativar") {
    Write-Host "Ativando Otimizacoes de Memoria RAM..." -ForegroundColor Cyan

    # Detectar RAM Física total em GB e KB
    $TotalRAM = (Get-CimInstance Win32_PhysicalMemory -ErrorAction SilentlyContinue | Measure-Object -Property Capacity -Sum).Sum / 1GB
    if (!$TotalRAM -or $TotalRAM -eq 0) {
        $TotalRAM = (Get-WmiObject -Class Win32_PhysicalMemory -ErrorAction SilentlyContinue | Measure-Object -Property Capacity -Sum).Sum / 1GB
    }

    $RAMinKB = (Get-CimInstance Win32_PhysicalMemory -ErrorAction SilentlyContinue | Measure-Object -Property Capacity -Sum).Sum / 1KB
    if (!$RAMinKB -or $RAMinKB -eq 0) {
        $RAMinKB = (Get-WmiObject -Class Win32_PhysicalMemory -ErrorAction SilentlyContinue | Measure-Object -Property Capacity -Sum).Sum / 1KB
    }

    # 1. Compressão de Memória (Disable-MMAgent)
    if ($TotalRAM -ge 15.5) {
        Write-Host "[1/5] Detectado $TotalRAM GB de RAM. Desativando Compressão de Memória..." -ForegroundColor Green
        Disable-MMAgent -MemoryCompression -ErrorAction SilentlyContinue
    } else {
        Write-Host "[1/5] Detectado $TotalRAM GB de RAM. Mantendo Compressão ativa por segurança..." -ForegroundColor Yellow
        Enable-MMAgent -MemoryCompression -ErrorAction SilentlyContinue
    }

    # 2. Desativar Page Combining (Economiza ciclos de CPU)
    Write-Host "[2/5] Desativando Page Combining (Fusao de paginas em segundo plano)..." -ForegroundColor Yellow
    Disable-MMAgent -PageCombining -ErrorAction SilentlyContinue
    Set-MMAgent -MaxOperationAPIFiles 2048 -ErrorAction SilentlyContinue

    # 3. DisablePagingExecutive (Força o Kernel e os drivers a ficarem na RAM rápida)
    Write-Host "[3/5] Forcando o Kernel e drivers a residirem estritamente na RAM..." -ForegroundColor Yellow
    if (!(Test-Path $RegistryMemory)) { New-Item -Path $RegistryMemory -Force | Out-Null }
    Set-ItemProperty -Path $RegistryMemory -Name "DisablePagingExecutive" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue

    # 4. IoPageLockLimit (Otimiza buffer de leitura/escrita I/O na RAM)
    Write-Host "[4/5] Otimizando buffers de I/O de memoria..." -ForegroundColor Yellow
    Set-ItemProperty -Path $RegistryMemory -Name "IoPageLockLimit" -Value 16710656 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $RegistryMemory -Name "LargeSystemCache" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue

    # 5. SvcHostSplitThresholdInKB (Reagrupar processos svchost.exe para liberar RAM e diminuir Context Switches)
    if ($RAMinKB -gt 0) {
        Write-Host "[5/5] Reagrupando processos svchost.exe (SvcHost Split) para o limite de $($TotalRAM)GB..." -ForegroundColor Yellow
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control" -Name "SvcHostSplitThresholdInKB" -Value $RAMinKB -Type DWord -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "[5/5] Capacidade de RAM nao detectada para SvcHost Split. Pulando..." -ForegroundColor Yellow
    }

    Write-Host "`n[OK] Otimizacoes de Memoria RAM aplicadas com sucesso!" -ForegroundColor Green

} elseif ($Acao -eq "Reverter") {
    Write-Host "Revertendo Otimizacoes de Memoria RAM..." -ForegroundColor Cyan

    # 1. Reativar compressão de RAM
    Write-Host "[1/5] Reativando Compressao de Memoria..." -ForegroundColor Yellow
    Enable-MMAgent -MemoryCompression -ErrorAction SilentlyContinue

    # 2. Reativar Page Combining
    Write-Host "[2/5] Reativando Page Combining e restaurando limites do MMAgent..." -ForegroundColor Yellow
    Enable-MMAgent -PageCombining -ErrorAction SilentlyContinue
    Set-MMAgent -MaxOperationAPIFiles 256 -ErrorAction SilentlyContinue

    # 3. Restaurar paginação do Kernel (DisablePagingExecutive)
    Write-Host "[3/5] Permitindo paginacao do Kernel e drivers no disco..." -ForegroundColor Yellow
    if (Test-Path $RegistryMemory) {
        Set-ItemProperty -Path $RegistryMemory -Name "DisablePagingExecutive" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    # 4. Remover chaves customizadas de buffers
    Write-Host "[4/5] Restaurando buffers de I/O padrao..." -ForegroundColor Yellow
    if (Test-Path $RegistryMemory) {
        Remove-ItemProperty -Path $RegistryMemory -Name "IoPageLockLimit" -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $RegistryMemory -Name "LargeSystemCache" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    }

    # 5. Restaurar agrupamento padrao de processos svchost.exe
    Write-Host "[5/5] Restaurando limite padrao de isolamento de processos svchost.exe..." -ForegroundColor Yellow
    Remove-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control" -Name "SvcHostSplitThresholdInKB" -ErrorAction SilentlyContinue

    Write-Host "`n[OK] Otimizacoes de Memoria RAM revertidas para o padrao!" -ForegroundColor Green
}
