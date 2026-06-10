param([string]$Acao = "Ativar")

$TimelinePath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System"
$NewsPath = "HKLM:\SOFTWARE\Policies\Microsoft"
$FeedsPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Feeds"
$CdmPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"

if ($Acao -eq "Ativar") {
    Write-Host "Desativando Historico de Atividades (Linha do Tempo) e Widgets..." -ForegroundColor Yellow

    # Desativar Linha do Tempo (Activity Feed)
    if (!(Test-Path $TimelinePath)) { New-Item -Path $TimelinePath -Force | Out-Null }
    Set-ItemProperty -Path $TimelinePath -Name "EnableActivityFeed" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $TimelinePath -Name "PublishUserActivities" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $TimelinePath -Name "UploadUserActivities" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    # Desativar Widgets e Noticias da Barra de Tarefas (News & Interests)
    if (!(Test-Path $NewsPath)) { New-Item -Path $NewsPath -Force | Out-Null }
    Set-ItemProperty -Path $NewsPath -Name "AllowNewsAndInterests" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    if (!(Test-Path $FeedsPath)) { New-Item -Path $FeedsPath -Force | Out-Null }
    Set-ItemProperty -Path $FeedsPath -Name "EnableFeeds" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    # Desativar sugestões e conteúdo de terceiros no feed
    if (!(Test-Path $CdmPath)) { New-Item -Path $CdmPath -Force | Out-Null }
    Set-ItemProperty -Path $CdmPath -Name "SubscribedContent-310093Enabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

    Write-Host "Concluido! Historico de atividades e widgets foram desativados." -ForegroundColor Green
} else {
    Write-Host "Revertendo Linha do Tempo e Widgets para o padrao do Windows..." -ForegroundColor Yellow

    if (Test-Path $TimelinePath) {
        Remove-ItemProperty -Path $TimelinePath -Name "EnableActivityFeed" -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $TimelinePath -Name "PublishUserActivities" -Force -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $TimelinePath -Name "UploadUserActivities" -Force -ErrorAction SilentlyContinue
    }

    if (Test-Path $NewsPath) {
        Remove-ItemProperty -Path $NewsPath -Name "AllowNewsAndInterests" -Force -ErrorAction SilentlyContinue
    }

    if (Test-Path $FeedsPath) {
        Remove-ItemProperty -Path $FeedsPath -Name "EnableFeeds" -Force -ErrorAction SilentlyContinue
    }

    if (Test-Path $CdmPath) {
        Remove-ItemProperty -Path $CdmPath -Name "SubscribedContent-310093Enabled" -Force -ErrorAction SilentlyContinue
    }

    Write-Host "Concluido! As configuracoes foram restauradas para o padrao do Windows." -ForegroundColor Green
}
