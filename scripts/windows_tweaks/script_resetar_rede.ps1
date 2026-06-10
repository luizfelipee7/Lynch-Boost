# Requer privilegios de administrador
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Este script precisa ser executado como Administrador!"
    exit
}

Write-Host "Iniciando redefinicao completa da pilha de rede..."
Write-Host "--------------------------------------------------------"

# 1. Redefinindo o catalogo do Winsock
Write-Host "[1/4] Redefinindo o catalogo do Winsock..."
netsh winsock reset >$null 2>&1
Write-Host "✓ Catalogo do Winsock restaurado com sucesso!"

# 2. Redefinindo o protocolo TCP/IP
Write-Host "[2/4] Restaurando configuracoes padrao do protocolo TCP/IP..."
netsh int ip reset >$null 2>&1
Write-Host "✓ Configuracoes de TCP/IP restauradas com sucesso!"

# 3. Liberando e limpando configuracoes de IP e cache DNS
Write-Host "[3/4] Liberando enderecos IP locais e limpando Cache DNS..."
ipconfig /release >$null 2>&1
Clear-DnsClientCache -ErrorAction SilentlyContinue
ipconfig /flushdns >$null 2>&1
Write-Host "✓ Cache DNS limpo e conexoes antigas liberadas!"

# 4. Renovando concessao de IP DHCP
Write-Host "[4/4] Solicitando nova concessao de IP (DHCP) ao roteador..."
ipconfig /renew >$null 2>&1
Write-Host "✓ Enderecos IP locais renovados com sucesso!"

Write-Host "--------------------------------------------------------"
Write-Host "Redefinicao concluida com sucesso!" -ForegroundColor Green
Write-Host "E obrigatorio reiniciar o computador para aplicar as alteracoes!" -ForegroundColor Yellow
