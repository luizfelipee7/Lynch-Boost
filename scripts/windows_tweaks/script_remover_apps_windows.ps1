#Requires -Version 5.1

param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$CatalogPath,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Ids
)

$ErrorActionPreference = "Continue"
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Status {
    param(
        [AllowEmptyString()]
        [string]$Message = ""
    )

    Write-Host $Message
}

function Assert-Administrator {
    $principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
        throw "Este script precisa ser executado como administrador."
    }
}

function Get-CatalogItems {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Catalogo nao encontrado: $Path"
    }

    $catalog = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    $items = @{}

    foreach ($group in $catalog.PSObject.Properties) {
        foreach ($item in @($group.Value)) {
            if ($null -eq $item.id) {
                continue
            }
            $items[[string]$item.id] = $item
        }
    }

    return $items
}

function Set-RegistryValue {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Entry
    )

    $path = [string]$Entry.path
    $name = [string]$Entry.name
    $type = [string]$Entry.type
    $value = $Entry.value

    if (-not (Test-Path -LiteralPath $path)) {
        New-Item -Path $path -Force | Out-Null
    }

    if (Get-ItemProperty -Path $path -Name $name -ErrorAction SilentlyContinue) {
        Set-ItemProperty -Path $path -Name $name -Value $value -Force
    }
    else {
        New-ItemProperty -Path $path -Name $name -Value $value -PropertyType $type -Force | Out-Null
    }
    Write-Status "Politica aplicada: $path\$name=$value"
}

function Disable-ServiceIfPresent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $service = Get-Service -Name $Name -ErrorAction SilentlyContinue
    if ($null -eq $service) {
        Write-Status "Servico nao encontrado: $Name"
        return
    }

    Stop-Service -Name $Name -Force -ErrorAction SilentlyContinue
    Set-Service -Name $Name -StartupType Disabled -ErrorAction SilentlyContinue
    Write-Status "Servico desativado: $Name"
}

function Remove-AppxSelector {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Selector,

        [switch]$Pattern
    )

    if ($Pattern) {
        $provisioned = Get-AppxProvisionedPackage -Online | Where-Object { $_.DisplayName -like $Selector }
        $installed = Get-AppxPackage -AllUsers | Where-Object { $_.Name -like $Selector }
    }
    else {
        $provisioned = Get-AppxProvisionedPackage -Online | Where-Object { $_.DisplayName -eq $Selector }
        $installed = Get-AppxPackage -AllUsers | Where-Object { $_.Name -eq $Selector }
    }

    if ($provisioned) {
        foreach ($package in $provisioned) {
            Write-Status "Removendo provisionado: $($package.DisplayName)"
            $package | Remove-AppxProvisionedPackage -AllUsers -Online -ErrorAction Continue | Out-Null
        }
    }
    else {
        Write-Status "Provisionado nao encontrado: $Selector"
    }

    if ($installed) {
        foreach ($package in $installed) {
            Write-Status "Removendo instalado: $($package.Name)"
            $package | Remove-AppxPackage -AllUsers -ErrorAction Continue | Out-Null
        }
    }
    else {
        Write-Status "Instalado nao encontrado: $Selector"
    }
}

function Remove-FeatureSelector {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Selector
    )

    $feature = Get-WindowsOptionalFeature -Online |
        Where-Object { $_.FeatureName -eq $Selector -and $_.State -notin @("Disabled", "DisabledWithPayloadRemoved") }

    if ($null -eq $feature) {
        Write-Status "Recurso opcional nao ativo: $Selector"
        return
    }

    Write-Status "Removendo recurso opcional: $Selector"
    $feature | Disable-WindowsOptionalFeature -Online -Remove -NoRestart -ErrorAction Continue | Out-Null
}

function Remove-CapabilitySelector {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Selector
    )

    $capabilities = Get-WindowsCapability -Online |
        Where-Object {
            ($_.Name -split "~")[0] -eq $Selector -and
            $_.State -notin @("NotPresent", "Removed")
        }

    if ($null -eq $capabilities) {
        Write-Status "Capacidade nao ativa: $Selector"
        return
    }

    foreach ($capability in $capabilities) {
        Write-Status "Removendo capacidade: $($capability.Name)"
        $capability | Remove-WindowsCapability -Online -ErrorAction Continue | Out-Null
    }
}

function Remove-RegistryPathIfPresent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Force -Recurse -ErrorAction Continue
        Write-Status "Registro removido: $Path"
    }
    else {
        Write-Status "Registro nao encontrado: $Path"
    }
}

function Invoke-Removal {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Item
    )

    Write-Status ""
    Write-Status "Processando: $($Item.nome)"

    if ($Item.tipo -eq "especial") {
        Write-Status "Item especial ignorado pelo executor generico: $($Item.nome)"
        return
    }

    foreach ($selector in @($Item.appx_selectors)) {
        if (-not [string]::IsNullOrWhiteSpace([string]$selector)) {
            Remove-AppxSelector -Selector ([string]$selector)
        }
    }

    foreach ($pattern in @($Item.appx_patterns)) {
        if (-not [string]::IsNullOrWhiteSpace([string]$pattern)) {
            Remove-AppxSelector -Selector ([string]$pattern) -Pattern
        }
    }

    foreach ($capability in @($Item.capability_selectors)) {
        if (-not [string]::IsNullOrWhiteSpace([string]$capability)) {
            Remove-CapabilitySelector -Selector ([string]$capability)
        }
    }

    foreach ($feature in @($Item.feature_selectors)) {
        if (-not [string]::IsNullOrWhiteSpace([string]$feature)) {
            Remove-FeatureSelector -Selector ([string]$feature)
        }
    }

    foreach ($service in @($Item.services_to_disable)) {
        if (-not [string]::IsNullOrWhiteSpace([string]$service)) {
            Disable-ServiceIfPresent -Name ([string]$service)
        }
    }

    foreach ($entry in @($Item.registry_values)) {
        if ($null -ne $entry) {
            Set-RegistryValue -Entry $entry
        }
    }

    foreach ($path in @($Item.registry_delete_paths)) {
        if (-not [string]::IsNullOrWhiteSpace([string]$path)) {
            Remove-RegistryPathIfPresent -Path ([string]$path)
        }
    }
}

try {
    Assert-Administrator

    $catalogItems = Get-CatalogItems -Path $CatalogPath
    $idsToRemove = $Ids -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ }

    if (-not $idsToRemove) {
        throw "Nenhum ID informado para remocao."
    }

    foreach ($id in $idsToRemove) {
        if (-not $catalogItems.ContainsKey($id)) {
            throw "ID nao permitido pelo catalogo: $id"
        }
    }

    Write-Status "Iniciando remocao de aplicativos do Windows..."
    Write-Status "Total selecionado: $($idsToRemove.Count)"

    foreach ($id in $idsToRemove) {
        Invoke-Removal -Item $catalogItems[$id]
    }

    Write-Status ""
    Write-Status "Remocao de aplicativos concluida."
    exit 0
}
catch {
    Write-Status "[ERRO] $($_.Exception.Message)"
    exit 1
}
