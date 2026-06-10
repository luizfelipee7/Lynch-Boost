Write-Host "Iniciando a liberação e limpeza do Cache de Memória RAM (Standby List)..." -ForegroundColor Yellow

# Invoca a limpeza nativa de tarefas ociosas e gerenciamento de páginas do Windows em segundo plano
Start-Process -FilePath "rundll32.exe" -ArgumentList "advapi32.dll,ProcessIdleTasks"

# Executa a coleta de lixo de recursos do sistema
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

Write-Host "Concluído! O cache da memória RAM foi esvaziado com sucesso." -ForegroundColor Green
