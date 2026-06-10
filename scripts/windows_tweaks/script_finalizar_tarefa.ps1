param([string]$Acao = "Ativar")

if ($Acao -eq "Ativar") {
    Write-Host "[*] Injetando opcao no menu de contexto da barra de tarefas..."
    if (!(Test-Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings")) {
        New-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings" -Name "TaskbarEndTask" -Value 1 -Force
    Write-Host "Concluido! Reinicie o computador para aplicar as mudancas."
} else {
    Write-Host "[*] Removendo opcao no menu de contexto da barra de tarefas..."
    if (Test-Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings") {
        Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings" -Name "TaskbarEndTask" -Value 0 -Force
    }
    Write-Host "Concluido! Reinicie o computador para aplicar as mudancas."
}
