$ErrorActionPreference = "Stop"

Write-Host "========================================================"
Write-Host "      LYNCH FPS BOOST - EFEITOS VISUAIS DE DESEMPENHO"
Write-Host "========================================================"
Write-Host ""

$csharp = @"
using System;
using System.Runtime.InteropServices;

public class Win32VisualEffects {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, uint pvParam, uint fWinIni);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, ref uint pvParam, uint fWinIni);

    public const uint SPIF_UPDATEINIFILE = 0x01;
    public const uint SPIF_SENDCHANGE = 0x02;
    public const uint FLAGS = SPIF_UPDATEINIFILE | SPIF_SENDCHANGE;

    public const uint SPI_SETUIEFFECTS = 0x103F;
    public const uint SPI_SETANIMATION = 0x0049;
    public const uint SPI_SETDRAGFULLWINDOWS = 0x0025;
    public const uint SPI_SETFONTSMOOTHING = 0x004B;
    public const uint SPI_SETLISTBOXSMOOTHSCROLLING = 0x1007;
    public const uint SPI_SETMENUFADE = 0x1013;
    public const uint SPI_SETMENUANIMATION = 0x1003;
    public const uint SPI_SETCOMBOBOXANIMATION = 0x1005;
    public const uint SPI_SETTOOLTIPANIMATION = 0x1017;
    public const uint SPI_SETTOOLTIPFADE = 0x1019;
    public const uint SPI_SETCURSORSHADOW = 0x101B;
    public const uint SPI_SETDROPSHADOW = 0x1025;
    public const uint SPI_SETCLIENTAREAANIMATION = 0x1043;
    
    [StructLayout(LayoutKind.Sequential)]
    public struct ANIMATIONINFO {
        public uint cbSize;
        public int iMinAnimate;
    }

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, ref ANIMATIONINFO pvParam, uint fWinIni);

    public static void ApplyLynchVisuals() {
        // Desligar efeitos de UI (Controles e Elementos, menus, tooltips, comboboxes)
        SystemParametersInfo(SPI_SETUIEFFECTS, 0, 0, FLAGS);
        SystemParametersInfo(SPI_SETMENUFADE, 0, 0, FLAGS);
        SystemParametersInfo(SPI_SETMENUANIMATION, 0, 0, FLAGS);
        SystemParametersInfo(SPI_SETCOMBOBOXANIMATION, 0, 0, FLAGS);
        SystemParametersInfo(SPI_SETTOOLTIPANIMATION, 0, 0, FLAGS);
        SystemParametersInfo(SPI_SETTOOLTIPFADE, 0, 0, FLAGS);
        SystemParametersInfo(SPI_SETCLIENTAREAANIMATION, 0, 0, FLAGS);

        // Desativar sombras
        SystemParametersInfo(SPI_SETCURSORSHADOW, 0, 0, FLAGS);
        SystemParametersInfo(SPI_SETDROPSHADOW, 0, 0, FLAGS);

        // Desativar arrastar conteudo
        SystemParametersInfo(SPI_SETDRAGFULLWINDOWS, 0, 0, FLAGS);

        // Desativar rolagem suave
        SystemParametersInfo(SPI_SETLISTBOXSMOOTHSCROLLING, 0, 0, FLAGS);

        // Desativar animacoes de janela (MinAnimate)
        ANIMATIONINFO anim = new ANIMATIONINFO();
        anim.cbSize = (uint)Marshal.SizeOf(anim);
        anim.iMinAnimate = 0; // OFF
        SystemParametersInfo(SPI_SETANIMATION, anim.cbSize, ref anim, FLAGS);

        // Ligar Font Smoothing (Sua solicitacao)
        SystemParametersInfo(SPI_SETFONTSMOOTHING, 1, 0, FLAGS);
    }
}
"@

Write-Host "Injetando motor Win32 nativo para desligar Animar Controles e Elementos..."
Add-Type -TypeDefinition $csharp -Language CSharp -IgnoreWarnings
[Win32VisualEffects]::ApplyLynchVisuals()

Write-Host "Modificando chaves de registro diretamente (Thumbnails e Taskbar)..."
$RegAdvanced = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
$RegDesktop = "HKCU:\Control Panel\Desktop"
$RegVisualEffects = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
$RegDWM = "HKCU:\Software\Microsoft\Windows\DWM"

Write-Host "Preservando suavizacao de fontes e ClearType..."
Set-ItemProperty -Path $RegDesktop -Name "FontSmoothing" -Value "2" -Type String -Force
Set-ItemProperty -Path $RegDesktop -Name "FontSmoothingType" -Value 2 -Type DWord -Force
Set-ItemProperty -Path $RegDesktop -Name "FontSmoothingGamma" -Value 1200 -Type DWord -Force
Set-ItemProperty -Path $RegDesktop -Name "FontSmoothingOrientation" -Value 1 -Type DWord -Force

# Define Custom (3)
Set-ItemProperty -Path $RegVisualEffects -Name "VisualFXSetting" -Value 3 -Type DWord -Force

# Ligar miniaturas (IconsOnly = 0) (Sua solicitacao)
Set-ItemProperty -Path $RegAdvanced -Name "IconsOnly" -Value 0 -Type DWord -Force

# Desligar outros efeitos persistentes no Explorer
Set-ItemProperty -Path $RegAdvanced -Name "ListviewAlphaSelect" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $RegAdvanced -Name "ListviewShadow" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $RegAdvanced -Name "TaskbarAnimations" -Value 0 -Type DWord -Force

# Salvar visualizacoes de miniaturas da barra de tarefas (OFF) -> AlwaysHibernateThumbnails = 0
if (-not (Test-Path $RegDWM)) { New-Item -Path $RegDWM -Force | Out-Null }
Set-ItemProperty -Path $RegDWM -Name "AlwaysHibernateThumbnails" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $RegDWM -Name "EnableAeroPeek" -Value 0 -Type DWord -Force

Write-Host "Atualizando a mascara principal do UserPreferencesMask de forma limpa..."
# 90 12 03 80 10 00 00 00
$mask = [byte[]](0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00)
Set-ItemProperty -Path $RegDesktop -Name "UserPreferencesMask" -Value $mask -Force

Write-Host "Configuracoes aplicadas via API nativa e Registro em tempo real."
Write-Host "Desta vez, nao matamos o explorer para evitar que o Windows corrompa a memoria!"

# Avisar os processos do Windows sobre as mudancas no registro
# Isso diz ao Explorer para recarregar as definicoes de registro avançadas sem precisar reiniciar o PC.
$code = @"
using System;
using System.Runtime.InteropServices;
public class EnvironmentUpdater {
    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
}
"@
Add-Type -TypeDefinition $code -Language CSharp
[EnvironmentUpdater]::SendMessageTimeout([IntPtr]0xFFFF, 0x1A, [UIntPtr]::Zero, "Environment", 2, 5000, [ref][UIntPtr]::Zero) | Out-Null

Write-Host "========================================================"
Write-Host "OK - Efeitos Visuais rigorosamente ajustados com sucesso!"
Write-Host "========================================================"
exit 0
