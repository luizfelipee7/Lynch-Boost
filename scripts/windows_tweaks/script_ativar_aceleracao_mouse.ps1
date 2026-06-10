# Requer privilegios de Administrador para garantir aplicacao global
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Output "Ativando 'Aprimorar Precisao do Ponteiro' (Aceleracao de Mouse)..."

# Modificar o Registro do Windows para ligar a aceleracao do mouse (padrao do Windows)
Set-ItemProperty -Path "HKCU:\Control Panel\Mouse" -Name "MouseSpeed" -Value "1" -Type String -Force
Set-ItemProperty -Path "HKCU:\Control Panel\Mouse" -Name "MouseThreshold1" -Value "6" -Type String -Force
Set-ItemProperty -Path "HKCU:\Control Panel\Mouse" -Name "MouseThreshold2" -Value "10" -Type String -Force

# Restaurar as curvas padrao do Windows para aceleracao de mouse
$DefaultInputX = "00,00,00,00,00,00,00,00,15,e6,00,00,00,00,00,00,00,a0,01,00,00,00,00,00,00,40,02,00,00,00,00,00,00,e0,03,00,00,00,00,00"
$DefaultInputY = "00,00,00,00,00,00,00,00,b8,5e,01,00,00,00,00,00,00,a0,02,00,00,00,00,00,00,40,05,00,00,00,00,00,00,c0,0a,00,00,00,00,00"
$RegPath = 'HKCU:\Control Panel\Mouse'
$hexifiedX = $DefaultInputX.Split(',') | ForEach-Object { "0x$_" }
$hexifiedY = $DefaultInputY.Split(',') | ForEach-Object { "0x$_" }
Set-ItemProperty -Path $RegPath -Name "SmoothMouseXCurve" -Type Binary -Value (([byte[]]$hexifiedX)) -Force -ErrorAction SilentlyContinue
Set-ItemProperty -Path $RegPath -Name "SmoothMouseYCurve" -Type Binary -Value (([byte[]]$hexifiedY)) -Force -ErrorAction SilentlyContinue

# Codigo C# inline para chamar a API do Windows e aplicar a mudança na hora sem precisar reiniciar
Add-Type @"
using System.Runtime.InteropServices;
public class MouseConfig {
    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, int[] pvParam, uint fWinIni);
}
"@ -ErrorAction SilentlyContinue

# SPI_SETMOUSE = 0x0004
# Ativar aceleracao com os valores padrao (6, 10, 1)
# SPIF_UPDATEINIFILE = 0x01 | SPIF_SENDCHANGE = 0x02 -> 3
[MouseConfig]::SystemParametersInfo(0x0004, 0, [int[]]@(6,10,1), 3) | Out-Null

Write-Output "Aceleracao de mouse ativada e aplicada com sucesso!"
