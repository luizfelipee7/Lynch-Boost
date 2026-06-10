# ========================================================
# LYNCH FPS BOOST - DEBLOAT WINDOWS 11 MODERNO
# ========================================================
Write-Host "Iniciando limpeza profunda do Windows 11..." -ForegroundColor Cyan

# 1. Remocao de IA, Copilot e Recall
Write-Host "`n[1/3] Removendo modulos de Inteligencia Artificial (Copilot/Recall)..." -ForegroundColor Yellow
Get-AppxPackage -AllUsers *Copilot* | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
Get-AppxPackage -AllUsers Microsoft.MicrosoftOfficeHub | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
Set-Service -Name WSAIFabricSvc -StartupType Disabled -ErrorAction SilentlyContinue
Disable-WindowsOptionalFeature -FeatureName Recall -Online -Remove -NoRestart -ErrorAction SilentlyContinue | Out-Null
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f > $null 2>&1

# 2. Remocao de Widgets
Write-Host "`n[2/3] Matando e removendo Widgets (Clima/Noticias)..." -ForegroundColor Yellow
Get-Process *Widget* | Stop-Process -Force -ErrorAction SilentlyContinue
Get-AppxPackage Microsoft.WidgetsPlatformRuntime -AllUsers | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
Get-AppxPackage MicrosoftWindows.Client.WebExperience -AllUsers | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue

# 3. Limpeza de Appx (Excluindo tudo relacionado ao XBox)
Write-Host "`n[3/3] Limpando aplicativos inuteis pre-instalados (Mantendo XBox intacto)..." -ForegroundColor Yellow

$bloatwares = @(
    "Microsoft.549981C3F5F10",
    "Microsoft.BingNews",
    "Microsoft.BingWeather",
    "Microsoft.Getstarted",
    "Microsoft.Microsoft3DViewer",
    "Microsoft.MicrosoftSolitaireCollection",
    "Microsoft.MixedReality.Portal",
    "Microsoft.People",
    "Microsoft.SkypeApp",
    "Microsoft.WindowsAlarms",
    "Microsoft.WindowsCamera",
    "Microsoft.windowscommunicationsapps",
    "Microsoft.WindowsFeedbackHub",
    "Microsoft.WindowsMaps",
    "Microsoft.WindowsSoundRecorder",
    "Microsoft.ZuneVideo",
    "Microsoft.ZuneMusic",
    "Microsoft.Todos",
    # Novos itens seguros importados e refinados do EXM
    "Microsoft.GetHelp",
    "Microsoft.Messaging",
    "Microsoft.OneConnect",
    "Microsoft.Print3D",
    "Microsoft.3dBuilder",
    "Microsoft.BingFinance",
    "Microsoft.BingSports",
    "Microsoft.CommsPhone",
    "Microsoft.Sway",
    "Microsoft.WindowsPhone"
)

foreach ($app in $bloatwares) {
    Get-AppxPackage -AllUsers $app | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
}

Write-Host "`nLimpeza concluida com sucesso! O Windows 11 esta muito mais leve." -ForegroundColor Green
Start-Sleep -Seconds 5
