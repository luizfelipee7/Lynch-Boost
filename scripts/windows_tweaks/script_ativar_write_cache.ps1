# Requer privilegios de Administrador para garantir aplicacao global
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Output "Ativando Cache de Gravacao do Windows para Unidades de Disco..."

# Procurar todas as chaves de discos sob HKLM:\SYSTEM\CurrentControlSet\Enum
$ClassGuid = "{4d36e967-e325-11ce-bfc1-08002be10318}"
$EnumPath = "HKLM:\SYSTEM\CurrentControlSet\Enum"

# Buscar recursivamente as subchaves que contem os parametros de dispositivos de disco
Get-ChildItem -Path $EnumPath -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.PSChildName -eq "Device Parameters") {
        $DevicePath = $_.PSPath
        # Verificar se a chave pai e de um dispositivo de disco (ClassGUID correta)
        $ParentPath = Split-Path $DevicePath -Parent
        $ParentClass = (Get-ItemProperty -Path $ParentPath -Name "ClassGUID" -ErrorAction SilentlyContinue).ClassGUID
        
        if ($ParentClass -eq $ClassGuid) {
            $DiskPath = Join-Path $DevicePath "Disk"
            if (!(Test-Path $DiskPath)) {
                New-Item -Path $DiskPath -Force | Out-Null
            }
            # Ativar o Cache de Gravacao do Usuario
            Set-ItemProperty -Path $DiskPath -Name "UserWriteCacheSetting" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            Write-Output "Cache de Gravacao ativado para o dispositivo: $(Split-Path $ParentPath -Leaf)"
        }
    }
}

Write-Output "Concluido! Cache de Gravacao de Usuario habilitado com sucesso."
