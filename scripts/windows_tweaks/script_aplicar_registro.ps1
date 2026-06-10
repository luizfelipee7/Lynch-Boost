param (
    [Parameter(Mandatory=$true)]
    [string]$RegFile
)

# Regra Arquitetural Lynch: Forçar execução como Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Privilegios de Administrador necessarios. Reiniciando script com elevacao..."
    Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$PSCommandPath`" -RegFile `"$RegFile`"" -Verb RunAs
    exit
}

# Resolve o caminho absoluto do arquivo .reg
$BasePath = Split-Path -Parent $PSCommandPath
$RegFullPath = Join-Path -Path $BasePath -ChildPath $RegFile

if (-not (Test-Path -Path $RegFullPath)) {
    Write-Error "O arquivo de registro nao foi encontrado no caminho: $RegFullPath"
    exit 1
}

Write-Output "Aplicando arquivo de registro: $RegFile"
# Executa silenciosamente a importação do registro usando reg.exe
$process = Start-Process -FilePath "reg.exe" -ArgumentList "import `"$RegFullPath`"" -Wait -NoNewWindow -PassThru

if ($process.ExitCode -eq 0) {
    Write-Output "Registro aplicado com sucesso."
} else {
    Write-Error "Falha ao aplicar o registro. Codigo de saida: $($process.ExitCode)"
    exit 1
}
