# Requer privilegios de Administrador para garantir aplicacao global
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Output "Desativando 'Aprimorar Precisao do Ponteiro' (Aceleracao de Mouse)..."

# Modificar o Registro do Windows para desligar a aceleracao do mouse
Set-ItemProperty -Path "HKCU:\Control Panel\Mouse" -Name "MouseSpeed" -Value "0" -Type String -Force
Set-ItemProperty -Path "HKCU:\Control Panel\Mouse" -Name "MouseThreshold1" -Value "0" -Type String -Force
Set-ItemProperty -Path "HKCU:\Control Panel\Mouse" -Name "MouseThreshold2" -Value "0" -Type String -Force
Set-ItemProperty -Path "HKCU:\Control Panel\Mouse" -Name "MouseSensitivity" -Value "10" -Type String -Force

# Codigo C# inline para obter a escala de DPI da tela sem depender de System.Drawing.dll
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class DPIHelper {
    [DllImport("gdi32.dll")]
    public static extern int GetDeviceCaps(IntPtr hdc, int nIndex);
    [DllImport("user32.dll")]
    public static extern IntPtr GetDC(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);
}
"@ -ErrorAction SilentlyContinue

# 1. Obter a escala do monitor (DPI)
$ScreenScale = 100
try {
    # Primeira tentativa: via Registro do Windows (AppliedDPI)
    $AppliedDPI = (Get-ItemProperty -Path 'HKCU:\Control Panel\Desktop\WindowMetrics' -Name "AppliedDPI" -ErrorAction SilentlyContinue).AppliedDPI
    if ($AppliedDPI) {
        $ScreenScale = [math]::round(($AppliedDPI / 96) * 100)
    } else {
        # Segunda tentativa: fallback com APIs gdi32/user32 nativas
        $hDC = [DPIHelper]::GetDC([IntPtr]::Zero)
        $logicalY = [DPIHelper]::GetDeviceCaps($hDC, 10)  # VERTRES
        $physicalY = [DPIHelper]::GetDeviceCaps($hDC, 117) # DESKTOPVERTRES
        [void][DPIHelper]::ReleaseDC([IntPtr]::Zero, $hDC)
        if ($logicalY -gt 0 -and $physicalY -gt 0) {
            $ScreenScale = [math]::round(($physicalY / $logicalY) * 100)
        }
    }
} catch {
    $ScreenScale = 100
}

# 2. Definir as curvas binarias de paridade 1:1 do MarkC Mouse Fix de acordo com o DPI
$YourInputX = $null
$YourInputY = $null

switch ($ScreenScale) {
    100 {
        $YourInputX = "00,00,00,00,00,00,00,00,C0,CC,0C,00,00,00,00,00,80,99,19,00,00,00,00,00,40,66,26,00,00,00,00,00,00,33,33,00,00,00,00,00"
        $YourInputY = "00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,70,00,00,00,00,00,00,00,A8,00,00,00,00,00,00,00,E0,00,00,00,00,00"
    }
    125 {
        $YourInputX = "00,00,00,00,00,00,00,00,00,00,10,00,00,00,00,00,00,00,20,00,00,00,00,00,00,00,30,00,00,00,00,00,00,00,40,00,00,00,00,00"
        $YourInputY = "00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,70,00,00,00,00,00,00,00,A8,00,00,00,00,00,00,00,E0,00,00,00,00,00"
    }
    150 {
        $YourInputX = "00,00,00,00,00,00,00,00,30,33,13,00,00,00,00,00,60,66,26,00,00,00,00,00,90,99,39,00,00,00,00,00,C0,CC,4C,00,00,00,00,00"
        $YourInputY = "00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,70,00,00,00,00,00,00,00,A8,00,00,00,00,00,00,00,E0,00,00,00,00,00"
    }
    175 {
        $YourInputX = "00,00,00,00,00,00,00,00,60,66,16,00,00,00,00,00,C0,CC,2C,00,00,00,00,00,20,33,43,00,00,00,00,00,80,99,59,00,00,00,00,00"
        $YourInputY = "00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,70,00,00,00,00,00,00,00,A8,00,00,00,00,00,00,00,E0,00,00,00,00,00"
    }
    200 {
        $YourInputX = "00,00,00,00,00,00,00,00,90,99,19,00,00,00,00,00,20,33,33,00,00,00,00,00,B0,CC,4C,00,00,00,00,00,40,66,66,00,00,00,00,00"
        $YourInputY = "00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,70,00,00,00,00,00,00,00,A8,00,00,00,00,00,00,00,E0,00,00,00,00,00"
    }
    225 {
        $YourInputX = "00,00,00,00,00,00,00,00,C0,CC,1C,00,00,00,00,00,80,99,39,00,00,00,00,00,40,66,56,00,00,00,00,00,00,33,73,00,00,00,00,00"
        $YourInputY = "00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,70,00,00,00,00,00,00,00,A8,00,00,00,00,00,00,00,E0,00,00,00,00,00"
    }
    250 {
        $YourInputX = "00,00,00,00,00,00,00,00,00,00,20,00,00,00,00,00,00,00,40,00,00,00,00,00,00,00,60,00,00,00,00,00,00,00,80,00,00,00,00,00"
        $YourInputY = "00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,70,00,00,00,00,00,00,00,A8,00,00,00,00,00,00,00,E0,00,00,00,00,00"
    }
    300 {
        $YourInputX = "00,00,00,00,00,00,00,00,60,66,26,00,00,00,00,00,C0,CC,4C,00,00,00,00,00,20,33,73,00,00,00,00,00,80,99,99,00,00,00,00,00"
        $YourInputY = "00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,70,00,00,00,00,00,00,00,A8,00,00,00,00,00,00,00,E0,00,00,00,00,00"
    }
    350 {
        $YourInputX = "00,00,00,00,00,00,00,00,C0,CC,2C,00,00,00,00,00,80,99,59,00,00,00,00,00,40,66,86,00,00,00,00,00,00,33,B3,00,00,00,00,00"
        $YourInputY = "00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,70,00,00,00,00,00,00,00,A8,00,00,00,00,00,00,00,E0,00,00,00,00,00"
    }
    default {
        # Fallback padrao de 100%
        Write-Warning "Escala de DPI nao tradicional detectada ($ScreenScale%). Usando perfil de 100% como fallback seguro."
        $YourInputX = "00,00,00,00,00,00,00,00,C0,CC,0C,00,00,00,00,00,80,99,19,00,00,00,00,00,40,66,26,00,00,00,00,00,00,33,33,00,00,00,00,00"
        $YourInputY = "00,00,00,00,00,00,00,00,00,00,38,00,00,00,00,00,00,00,70,00,00,00,00,00,00,00,A8,00,00,00,00,00,00,00,E0,00,00,00,00,00"
    }
}

if ($YourInputX -and $YourInputY) {
    Write-Output "Escala de DPI detectada: $ScreenScale% - Aplicando Curva de Paridade de Mouse MarkC..."
    $RegPath = 'HKCU:\Control Panel\Mouse'
    $hexifiedX = $YourInputX.Split(',') | ForEach-Object { "0x$_" }
    $hexifiedY = $YourInputY.Split(',') | ForEach-Object { "0x$_" }
    Set-ItemProperty -Path $RegPath -Name "SmoothMouseXCurve" -Type Binary -Value (([byte[]]$hexifiedX)) -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $RegPath -Name "SmoothMouseYCurve" -Type Binary -Value (([byte[]]$hexifiedY)) -Force -ErrorAction SilentlyContinue
}

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
# SPIF_UPDATEINIFILE = 0x01 | SPIF_SENDCHANGE = 0x02 -> 3
[MouseConfig]::SystemParametersInfo(0x0004, 0, [int[]]@(0,0,0), 3) | Out-Null

Write-Output "Aceleracao de mouse desativada e aplicada com sucesso com paridade MarkC 1:1!"
