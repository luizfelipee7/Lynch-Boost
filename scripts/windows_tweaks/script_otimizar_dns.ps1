param(
    [string]$DNS_Mode = "Cloudflare",
    [string]$Primary = $null,
    [string]$Secondary = $null
)

Write-Host "Iniciando otimizacao de DNS (Modo: $DNS_Mode)..."

# Requer privilégios de administrador
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Este script precisa ser executado como Administrador!"
    exit
}

$interfaces = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
if ($interfaces.Count -eq 0) {
    Write-Warning "Nenhum adaptador de rede ativo encontrado."
    exit
}

function Disable-IPv6 {
    foreach ($interface in $interfaces) {
        Write-Host "Desativando IPv6 em $($interface.Name) para evitar conflitos de rota DNS..."
        Disable-NetAdapterBinding -Name $interface.Name -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue
    }
}

function Enable-IPv6 {
    foreach ($interface in $interfaces) {
        Write-Host "Reativando IPv6 em $($interface.Name)..."
        Enable-NetAdapterBinding -Name $interface.Name -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue
    }
}

function Set-DNS {
    param($Primary, $Secondary, $Name)
    
    # Desativa IPv6 para forçar o Windows a usar o DNS IPv4 otimizado
    Disable-IPv6
    
    foreach ($interface in $interfaces) {
        Write-Host "Configurando $($interface.Name) para $Name ($Primary / $Secondary)..."
        Set-DnsClientServerAddress -InterfaceIndex $interface.ifIndex -ServerAddresses ($Primary, $Secondary) -ErrorAction SilentlyContinue
    }
}

switch ($DNS_Mode) {
    "Cloudflare" { Set-DNS -Primary "1.1.1.1" -Secondary "1.0.0.1" -Name "Cloudflare DNS" }
    "Google"     { Set-DNS -Primary "8.8.8.8" -Secondary "8.8.4.4" -Name "Google DNS" }
    "Quad9"      { Set-DNS -Primary "9.9.9.9" -Secondary "149.112.112.112" -Name "Quad9 DNS" }
    "OpenDNS"    { Set-DNS -Primary "208.67.222.222" -Secondary "208.67.220.220" -Name "OpenDNS" }
    "AdGuard"    { Set-DNS -Primary "94.140.14.14" -Secondary "94.140.15.15" -Name "AdGuard DNS" }
    "Custom" {
        if ($Primary -and $Secondary) {
            Set-DNS -Primary $Primary -Secondary $Secondary -Name "DNS Personalizado"
        } else {
            Write-Warning "IPs de DNS primario e secundario nao fornecidos para o modo Custom."
        }
    }
    "Reset" {
        # Reativa o IPv6 ao voltar para o padrão
        Enable-IPv6
        foreach ($interface in $interfaces) {
            Write-Host "Restaurando $($interface.Name) para DHCP..."
            Set-DnsClientServerAddress -InterfaceIndex $interface.ifIndex -ResetServerAddresses -ErrorAction SilentlyContinue
        }
    }
    "Flush" {
        Write-Host "Apenas limpando o cache..."
    }
    default {
        Write-Warning "Modo invalido. Usando Flush apenas."
    }
}

Write-Host "Limpando Cache DNS (Flush DNS)..."
Clear-DnsClientCache
ipconfig /flushdns | Out-Null
Write-Host "Concluido com sucesso!" -ForegroundColor Green
