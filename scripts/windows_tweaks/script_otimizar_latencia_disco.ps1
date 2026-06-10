# ========================================================
# LYNCH FPS BOOST - OTIMIZAÇÃO DE LATÊNCIA DE DISCO (HIPM/DIPM)
# ========================================================
# Este script otimiza a latência física de leitura/escrita
# de SSDs e HDDs desativando economias de energia de link
# ativo (HIPM/DIPM) e gerenciamento ocioso do StorPort.
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
    Write-Host "Ativando Otimizacao de Latencia de Disco (SSDs/HDDs)..." -ForegroundColor Cyan

    # 1. Desativar EnableIdlePowerManagement em controladores StorPort
    Write-Host "[1/2] Desativando gerenciamento de energia ociosa do StorPort..." -ForegroundColor Yellow
    $StorPortKeys = Get-ChildItem -Path "HKLM:\SYSTEM\CurrentControlSet\Enum" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*StorPort*" }
    
    if ($StorPortKeys) {
        foreach ($key in $StorPortKeys) {
            Set-ItemProperty -Path $key.PSPath -Name "EnableIdlePowerManagement" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
        }
        Write-Host " -> OK: Ociosidade desativada em $($StorPortKeys.Count) chaves de hardware." -ForegroundColor Green
    } else {
        Write-Host " -> Nenhuma chave StorPort encontrada no registro." -ForegroundColor DarkGray
    }

    # 2. Desativar HIPM, DIPM e HDDParking nas portas de armazenamento dos serviços
    Write-Host "[2/2] Desativando economias de link ativo (HIPM/DIPM/HDDParking)..." -ForegroundColor Yellow
    $ServicesKeys = Get-ChildItem -Path "HKLM:\SYSTEM\CurrentControlSet\Services" -Recurse -ErrorAction SilentlyContinue
    
    $contagem = 0
    foreach ($key in $ServicesKeys) {
        $path = $key.PSPath
        $hasAny = $false
        
        if (Get-ItemProperty -Path $path -Name "EnableHIPM" -ErrorAction SilentlyContinue) {
            Set-ItemProperty -Path $path -Name "EnableHIPM" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
            $hasAny = $true
        }
        if (Get-ItemProperty -Path $path -Name "EnableDIPM" -ErrorAction SilentlyContinue) {
            Set-ItemProperty -Path $path -Name "EnableDIPM" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
            $hasAny = $true
        }
        if (Get-ItemProperty -Path $path -Name "EnableHDDParking" -ErrorAction SilentlyContinue) {
            Set-ItemProperty -Path $path -Name "EnableHDDParking" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
            $hasAny = $true
        }
        
        if ($hasAny) {
            $contagem++
        }
    }
    Write-Host " -> OK: Economias de energia desativadas em $contagem servicos de armazenamento." -ForegroundColor Green

    Write-Host "`n[OK] Otimizacoes de latencia de disco aplicadas com sucesso!" -ForegroundColor Green

} elseif ($Acao -eq "Reverter") {
    Write-Host "Revertendo Otimizacoes de Latencia de Disco..." -ForegroundColor Cyan

    # 1. Reativar StorPort Idle Power Management para o padrao (1)
    Write-Host "[1/2] Reativando gerenciamento de energia ociosa do StorPort..." -ForegroundColor Yellow
    $StorPortKeys = Get-ChildItem -Path "HKLM:\SYSTEM\CurrentControlSet\Enum" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*StorPort*" }
    
    if ($StorPortKeys) {
        foreach ($key in $StorPortKeys) {
            Set-ItemProperty -Path $key.PSPath -Name "EnableIdlePowerManagement" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
        }
        Write-Host " -> OK: Gerenciamento ocioso restaurado." -ForegroundColor Green
    }

    # 2. Reativar HIPM, DIPM e HDDParking para o padrao (1)
    Write-Host "[2/2] Reativando economias de link ativo (HIPM/DIPM/HDDParking)..." -ForegroundColor Yellow
    $ServicesKeys = Get-ChildItem -Path "HKLM:\SYSTEM\CurrentControlSet\Services" -Recurse -ErrorAction SilentlyContinue
    
    $contagem = 0
    foreach ($key in $ServicesKeys) {
        $path = $key.PSPath
        $hasAny = $false
        
        if (Get-ItemProperty -Path $path -Name "EnableHIPM" -ErrorAction SilentlyContinue) {
            Set-ItemProperty -Path $path -Name "EnableHIPM" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            $hasAny = $true
        }
        if (Get-ItemProperty -Path $path -Name "EnableDIPM" -ErrorAction SilentlyContinue) {
            Set-ItemProperty -Path $path -Name "EnableDIPM" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            $hasAny = $true
        }
        if (Get-ItemProperty -Path $path -Name "EnableHDDParking" -ErrorAction SilentlyContinue) {
            Set-ItemProperty -Path $path -Name "EnableHDDParking" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            $hasAny = $true
        }
        
        if ($hasAny) {
            $contagem++
        }
    }
    Write-Host " -> OK: Comportamento padrao reestabelecido em $contagem servicos." -ForegroundColor Green

    Write-Host "`n[OK] Otimizacoes de latencia de disco revertidas com sucesso!" -ForegroundColor Green
}
