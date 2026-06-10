# ========================================================
# LYNCH FPS BOOST - IMPORTADOR DE PERFIL NVIDIA
# ========================================================
# Requer privilegios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador!"
    exit 1
}

# Caminho relativo para encontrar o executavel do inspector e o perfil .nip
$NipPath = Join-Path -Path $PSScriptRoot -ChildPath "..\..\games\nvidia-profile\LynchBoostProfile.nip"
$InspectorPath = Join-Path -Path $PSScriptRoot -ChildPath "..\..\games\nvidia-profile\nvidiaProfileInspector.exe"

# Ativa a opção "Use as configurações de imagem avançadas em 3D" no painel da NVIDIA
$RegistryPath = "HKCU:\Software\NVIDIA Corporation\Global\NVTweak"
try {
    if (!(Test-Path $RegistryPath)) {
        New-Item -Path $RegistryPath -Force | Out-Null
    }
    Set-ItemProperty -Path $RegistryPath -Name "Gestalt" -Value 2 -Type DWord -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Opção 'Use as configurações de imagem avançadas em 3D' ativada no registro!" -ForegroundColor Green
} catch {
    Write-Warning "Não foi possível definir a opção de imagem 3D no registro: $_"
}

if (Test-Path $InspectorPath) {
    Write-Host "Importando perfil de otimizacao NVIDIA (LynchBoostProfile.nip)..." -ForegroundColor Yellow
    Start-Process -FilePath $InspectorPath -ArgumentList "-silentImport `"$NipPath`"" -Wait -NoNewWindow
    Write-Host "[OK] Perfil NVIDIA importado com sucesso!" -ForegroundColor Green
} else {
    Write-Error "[ERRO] nvidiaProfileInspector.exe nao encontrado em: $InspectorPath"
    exit 1
}

