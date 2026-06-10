# Requer privilegios de Administrador para modificar o registro
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$BasePath = Split-Path -Parent $PSCommandPath
$RegFile = Join-Path -Path $BasePath -ChildPath "script_cs2_high_priority.reg"

# Aplicar o arquivo .reg silenciosamente
$process = Start-Process -FilePath "reg.exe" -ArgumentList "import `"$RegFile`"" -Wait -NoNewWindow -PassThru

if ($process.ExitCode -eq 0) {
    Write-Output "CS2 High Priority Registry aplicado com sucesso."
} else {
    Write-Error "Falha ao aplicar o registro."
}


