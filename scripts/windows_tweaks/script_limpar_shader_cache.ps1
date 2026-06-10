# ========================================================
# LYNCH FPS BOOST - LIMPEZA DE CACHE DE SHADERS DE GPU
# ========================================================
# Este script realiza a exclusão dos caches de shaders de GPU
# (NVIDIA, AMD e Intel) para resolver stutters (travamentos).
# ========================================================

param (
    [ValidateSet("Ativar", "Reverter")]
    [string]$Acao = "Ativar"
)

# Requer privilégios de Administrador
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador!"
    exit 1
}

if ($Acao -eq "Ativar") {
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "   LYNCH FPS BOOST - LIMPEZA DE CACHES DE SHADERS GPU" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Fechando processos de jogos e launchers..." -ForegroundColor Yellow

    # Lista de processos comuns de launchers e jogos para encerrar temporariamente
    $processos = @("steam", "epicgameslauncher", "origin", "ea", "uplay", "battle.net", "discord", "chrome", "msedge", "brave")
    foreach ($p in $processos) {
        if (Get-Process -Name $p -ErrorAction SilentlyContinue) {
            Write-Host " -> Finalizando $p..." -ForegroundColor Gray
            Stop-Process -Name $p -Force -ErrorAction SilentlyContinue
        }
    }

    # Função auxiliar para limpar uma pasta
    function Limpar-Pasta {
        param (
            [string]$Caminho,
            [string]$Descricao
        )

        # Expandir qualquer variável de ambiente se necessário
        $caminhoExpandido = [System.Environment]::ExpandEnvironmentVariables($Caminho)

        if (Test-Path $caminhoExpandido) {
            Write-Host "Limpando $Descricao..." -ForegroundColor Yellow
            $itens = Get-ChildItem -Path $caminhoExpandido -Recurse -Force -ErrorAction SilentlyContinue
            $sucesso = 0
            $bloqueado = 0
            
            foreach ($item in $itens) {
                if ($item.PSIsContainer) { continue }
                try {
                    Remove-Item -Path $item.FullName -Force -ErrorAction Stop
                    $sucesso++
                } catch {
                    $bloqueado++
                }
            }
            
            # Deleta as subpastas que agora devem estar vazias
            $subpastas = Get-ChildItem -Path $caminhoExpandido -Directory -Recurse -Force -ErrorAction SilentlyContinue
            foreach ($pasta in ($subpastas | Sort-Object -Property FullName -Descending)) {
                try {
                    Remove-Item -Path $pasta.FullName -Force -Recurse -ErrorAction SilentlyContinue
                } catch {}
            }

            if ($sucesso -gt 0) {
                Write-Host "  -> OK: $sucesso arquivos de cache limpos." -ForegroundColor Green
            }
            if ($bloqueado -gt 0) {
                Write-Host "  -> Nota: $bloqueado arquivos em uso pelo sistema/driver (ignorado)." -ForegroundColor White
            }
            if ($sucesso -eq 0 -and $bloqueado -eq 0) {
                Write-Host "  -> Pasta ja se encontra vazia." -ForegroundColor Gray
            }
        } else {
            Write-Host "Pasta de cache $Descricao nao encontrada ou inativa." -ForegroundColor Gray
        }
    }

    # Caminhos de Cache de Shaders NVIDIA
    $nvidiaPaths = @(
        @{ Path = "%LOCALAPPDATA%\NVIDIA\DXCache"; Desc = "NVIDIA DirectX Cache (DXCache)" },
        @{ Path = "%LOCALAPPDATA%\NVIDIA\GLCache"; Desc = "NVIDIA OpenGL Cache (GLCache)" },
        @{ Path = "%LOCALAPPDATA%\NVIDIA\ComputeCache"; Desc = "NVIDIA Compute Cache" },
        @{ Path = "%LOCALAPPDATA%\NVIDIA\NV_Cache"; Desc = "NVIDIA NV_Cache" },
        @{ Path = "%APPDATA%\..\LocalLow\NVIDIA\PerDriverVersion\DXCache"; Desc = "NVIDIA LocalLow DXCache" },
        @{ Path = "%APPDATA%\..\LocalLow\NVIDIA\PerDriverVersion\GLCache"; Desc = "NVIDIA LocalLow GLCache" }
    )

    # Caminhos de Cache de Shaders AMD
    $amdPaths = @(
        @{ Path = "%LOCALAPPDATA%\AMD\DxCache"; Desc = "AMD DirectX Cache" },
        @{ Path = "%LOCALAPPDATA%\AMD\OglCache"; Desc = "AMD OpenGL Cache" },
        @{ Path = "%APPDATA%\..\LocalLow\AMD\DxCache"; Desc = "AMD LocalLow DxCache" },
        @{ Path = "%APPDATA%\..\LocalLow\AMD\OglCache"; Desc = "AMD LocalLow OglCache" }
    )

    # Caminhos de Cache de Shaders Intel
    $intelPaths = @(
        @{ Path = "%APPDATA%\..\LocalLow\Intel\ShaderCache"; Desc = "Intel Shader Cache" },
        @{ Path = "%LOCALAPPDATA%\Intel\ShaderCache"; Desc = "Intel Local Shader Cache" },
        @{ Path = "%LOCALAPPDATA%\Intel\GLCache"; Desc = "Intel OpenGL Cache" }
    )

    # Lista consolidada
    $gpuPaths = $nvidiaPaths + $amdPaths + $intelPaths

    Write-Host ""
    Write-Host "Executando varredura e limpeza..." -ForegroundColor Cyan
    foreach ($gpu in $gpuPaths) {
        Limpar-Pasta -Caminho $gpu.Path -Descricao $gpu.Desc
    }

    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "Limpeza de Shaders concluida com sucesso!" -ForegroundColor Green
    Write-Host "Nota: E perfeitamente normal que alguns arquivos em uso"
    Write-Host "pelo driver de video ou pelo Windows nao sejam apagados."
    Write-Host "========================================================" -ForegroundColor Cyan

} elseif ($Acao -eq "Reverter") {
    Write-Host "Revertendo Limpeza de Shaders da GPU..." -ForegroundColor Cyan
    Write-Host " -> Nota: Nao e possivel restaurar os arquivos de cache de shaders deletados." -ForegroundColor Yellow
    Write-Host " -> O Windows e o driver de video recriarao novos arquivos limpos automaticamente" -ForegroundColor Yellow
    Write-Host "    assim que você iniciar os seus jogos." -ForegroundColor Yellow
    Write-Host "`n[OK] Novo ciclo de compilacao limpa de shaders ativo!" -ForegroundColor Green
}
