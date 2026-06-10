param([string]$Acao = "Ativar")

$AdvancedPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
$AdInfoPath = "HKLM:\Software\Policies\Microsoft\Windows\AdvertisingInfo"
$CdmPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
$EngagementPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement"

if ($Acao -eq "Ativar") {
    Write-Host "Desativando pop-ups, dicas e sugestoes do Windows..." -ForegroundColor Yellow

    if (!(Test-Path $AdvancedPath)) { New-Item -Path $AdvancedPath -Force | Out-Null }
    Set-ItemProperty -Path $AdvancedPath -Name "DisallowShaking" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $AdvancedPath -Name "EnableBalloonTips" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $AdvancedPath -Name "ShowSyncProviderNotifications" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    if (!(Test-Path $AdInfoPath)) { New-Item -Path $AdInfoPath -Force | Out-Null }
    Set-ItemProperty -Path $AdInfoPath -Name "DisabledByGroupPolicy" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue

    if (!(Test-Path $CdmPath)) { New-Item -Path $CdmPath -Force | Out-Null }
    Set-ItemProperty -Path $CdmPath -Name "SoftLandingEnabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $CdmPath -Name "SubscribedContent-338389Enabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $CdmPath -Name "SubscribedContent-338388Enabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $CdmPath -Name "SubscribedContent-353696Enabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $CdmPath -Name "SystemPaneSuggestionsEnabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $CdmPath -Name "SubscribedContent-310093Enabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    if (!(Test-Path $EngagementPath)) { New-Item -Path $EngagementPath -Force | Out-Null }
    Set-ItemProperty -Path $EngagementPath -Name "ScoobeSystemSettingEnabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    Write-Host "Concluido! Todas as dicas e pop-ups irritantes foram silenciados." -ForegroundColor Green
} else {
    Write-Host "Revertendo configuracoes de pop-ups para o padrao do Windows..." -ForegroundColor Yellow

    if (Test-Path $AdvancedPath) {
        Remove-ItemProperty -Path $AdvancedPath -Name "DisallowShaking" -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $AdvancedPath -Name "EnableBalloonTips" -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $AdvancedPath -Name "ShowSyncProviderNotifications" -Force -ErrorAction SilentlyContinue
    }


    if (Test-Path $AdInfoPath) {
        Remove-ItemProperty -Path $AdInfoPath -Name "DisabledByGroupPolicy" -Force -ErrorAction SilentlyContinue
    }

    if (Test-Path $CdmPath) {
        Remove-ItemProperty -Path $CdmPath -Name "SoftLandingEnabled" -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $CdmPath -Name "SubscribedContent-338389Enabled" -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $CdmPath -Name "SubscribedContent-338388Enabled" -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $CdmPath -Name "SubscribedContent-353696Enabled" -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $CdmPath -Name "SystemPaneSuggestionsEnabled" -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $CdmPath -Name "SubscribedContent-310093Enabled" -Force -ErrorAction SilentlyContinue
    }

    if (Test-Path $EngagementPath) {
        Remove-ItemProperty -Path $EngagementPath -Name "ScoobeSystemSettingEnabled" -Force -ErrorAction SilentlyContinue
    }

    Write-Host "Concluido! Os pop-ups e dicas foram revertidos para o padrao do Windows." -ForegroundColor Green
}
