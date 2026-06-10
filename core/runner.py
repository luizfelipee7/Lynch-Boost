import ctypes
import json
import os
import shlex
import shutil
import subprocess
import tempfile

CREATE_NO_WINDOW = 0x08000000
POWERSHELL_EXE = "powershell.exe"
TERCEIROS_ISOLADOS = os.path.join("scripts", "otimizadores")

def executar_arquivo(caminho_arquivo, logger=None, argumentos_extras=""):
    diretorio_core = os.path.dirname(os.path.abspath(__file__))
    diretorio_raiz = os.path.dirname(diretorio_core)
    
    caminho_absoluto = os.path.abspath(os.path.join(diretorio_raiz, caminho_arquivo))

    if not _esta_dentro_do_projeto(caminho_absoluto, diretorio_raiz):
        _log(logger, f"[ERRO] Caminho fora do projeto bloqueado:\n{caminho_absoluto}")
        return False

    if _esta_em_terceiros_isolados(caminho_absoluto, diretorio_raiz):
        _log(logger, f"[ERRO] Execucao bloqueada: scripts de terceiros devem ser avaliados e migrados para windows_tweaks antes de uso.\n{caminho_absoluto}")
        return False

    if not os.path.exists(caminho_absoluto):
        if logger:
            logger(f"[ERRO] Arquivo nao encontrado:\n{caminho_absoluto}")
        return False

    argumentos = _normalizar_argumentos(argumentos_extras)
    extensao = os.path.splitext(caminho_absoluto)[1].lower()

    try:
        if _precisa_elevacao(extensao) and not _processo_elevado():
            return _executar_elevado_aguardando(caminho_absoluto, extensao, argumentos, logger, diretorio_raiz)

        comando = _montar_comando(caminho_absoluto, extensao, argumentos)
        _log(logger, f"Executando: {_formatar_comando(comando)}")
        processo = subprocess.Popen(
            comando, 
            shell=False, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            errors='replace',
            creationflags=CREATE_NO_WINDOW
        )
        
        if logger:
            for linha in processo.stdout:
                linha_limpa = linha.strip()
                if linha_limpa:  
                    logger(linha_limpa)
        
        processo.wait()
        if logger:
            logger(f"Processo finalizado com codigo de retorno: {processo.returncode}")
        return processo.returncode == 0
        
    except Exception as e:
        if logger:
            logger(f"[ERRO FATAL] Falha ao executar {caminho_absoluto}: {e}")
        return False


def _esta_dentro_do_projeto(caminho_absoluto, diretorio_raiz):
    try:
        return os.path.commonpath([caminho_absoluto, diretorio_raiz]) == diretorio_raiz
    except ValueError:
        return False


def _esta_em_terceiros_isolados(caminho_absoluto, diretorio_raiz):
    diretorio_terceiros = os.path.abspath(os.path.join(diretorio_raiz, TERCEIROS_ISOLADOS))
    try:
        return os.path.commonpath([caminho_absoluto, diretorio_terceiros]) == diretorio_terceiros
    except ValueError:
        return False


def _normalizar_argumentos(argumentos_extras):
    if argumentos_extras is None:
        return []
    if isinstance(argumentos_extras, (list, tuple)):
        return [str(argumento) for argumento in argumentos_extras]
    argumentos = str(argumentos_extras).strip()
    if not argumentos:
        return []
    return shlex.split(argumentos, posix=True)


def _precisa_elevacao(extensao):
    return extensao in {".ps1", ".bat", ".cmd", ".reg"}


def _processo_elevado():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _montar_comando(caminho_absoluto, extensao, argumentos):
    if extensao == ".ps1":
        return [
            POWERSHELL_EXE,
            "-ExecutionPolicy",
            "Bypass",
            "-NoProfile",
            "-NonInteractive",
            "-File",
            caminho_absoluto,
            *argumentos,
        ]
    if extensao in {".bat", ".cmd"}:
        return ["cmd.exe", "/d", "/c", "call", caminho_absoluto, *argumentos]
    if extensao == ".reg":
        return ["reg.exe", "import", caminho_absoluto]
    return [caminho_absoluto, *argumentos]


def _executar_elevado_aguardando(caminho_absoluto, extensao, argumentos, logger, diretorio_raiz):
    runner_temp_root = _preparar_diretorio_runner(diretorio_raiz)
    _limpar_runner_antigos(runner_temp_root)
    temp_dir = tempfile.mkdtemp(prefix="lynch_runner_", dir=runner_temp_root)
    config_path = os.path.join(temp_dir, "runner_config.json")
    runner_path = os.path.join(temp_dir, "runner_elevado.ps1")
    output_path = os.path.join(temp_dir, "runner_output.log")
    exit_code_path = os.path.join(temp_dir, "runner_exit_code.txt")

    config = {
        "target_path": caminho_absoluto,
        "target_type": extensao,
        "args": argumentos,
        "output_path": output_path,
        "exit_code_path": exit_code_path,
    }

    with open(config_path, "w", encoding="utf-8") as arquivo_config:
        json.dump(config, arquivo_config, ensure_ascii=False, indent=2)

    with open(runner_path, "w", encoding="utf-8") as arquivo_runner:
        arquivo_runner.write(_script_runner_elevado())

    with open(output_path, "w", encoding="utf-8"):
        pass

    with open(exit_code_path, "w", encoding="utf-8") as arquivo_codigo:
        arquivo_codigo.write("1")

    comando_bootstrap = [
        POWERSHELL_EXE,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-NonInteractive",
        "-Command",
        _script_bootstrap_elevado(runner_path, config_path, output_path, exit_code_path),
    ]

    processo = subprocess.Popen(
        comando_bootstrap,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        creationflags=CREATE_NO_WINDOW,
    )

    if processo.stdout:
        for linha in processo.stdout:
            linha_limpa = linha.strip()
            if linha_limpa:
                _log(logger, linha_limpa)

    processo.wait()
    _log(logger, f"Processo elevado finalizado com codigo de retorno: {processo.returncode}")
    sucesso = processo.returncode == 0
    _limpar_diretorio_temporario(temp_dir)
    return sucesso


def _script_bootstrap_elevado(runner_path, config_path, output_path, exit_code_path):
    runner_ps = _ps_string(runner_path)
    config_ps = _ps_string(config_path)
    output_ps = _ps_string(output_path)
    exit_code_ps = _ps_string(exit_code_path)
    powershell_ps = _ps_string(POWERSHELL_EXE)
    return f"""
$ErrorActionPreference = 'Stop'
try {{
    $argumentos = @(
        '-NoProfile',
        '-ExecutionPolicy',
        'Bypass',
        '-File',
        {runner_ps},
        '-ConfigPath',
        {config_ps}
    )
    $processo = Start-Process -FilePath {powershell_ps} -ArgumentList $argumentos -Verb RunAs -WindowStyle Hidden -Wait -PassThru
}} catch {{
    Write-Output ('[ERRO] Execucao elevada cancelada ou bloqueada: ' + $_.Exception.Message)
    exit 1223
}}

try {{
    if (Test-Path -LiteralPath {output_ps}) {{
        Get-Content -LiteralPath {output_ps} -Encoding UTF8 -ErrorAction Stop | ForEach-Object {{ Write-Output $_ }}
    }}
}} catch {{
}}

$codigoSaida = 1
try {{
    if (Test-Path -LiteralPath {exit_code_ps}) {{
        $conteudoCodigo = Get-Content -LiteralPath {exit_code_ps} -Raw -ErrorAction Stop
        if ([int]::TryParse($conteudoCodigo.Trim(), [ref]$codigoSaida) -eq $false) {{
            $codigoSaida = 1
        }}
    }} elseif ($null -ne $processo -and $null -ne $processo.ExitCode) {{
        $codigoSaida = [int]$processo.ExitCode
    }}
}} catch {{
    if ($null -ne $processo -and $null -ne $processo.ExitCode) {{
        $codigoSaida = [int]$processo.ExitCode
    }}
}}
exit $codigoSaida
""".strip()


def _script_runner_elevado():
    return r"""
param(
    [Parameter(Mandatory=$true)]
    [string]$ConfigPath
)

$ErrorActionPreference = 'Continue'

function Write-RunnerLog {
    param([string]$Mensagem)
    Add-Content -LiteralPath $script:OutputPath -Value $Mensagem -Encoding UTF8
}

try {
    $config = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $script:OutputPath = [string]$config.output_path
    $exitCodePath = [string]$config.exit_code_path
    $targetPath = [string]$config.target_path
    $targetType = [string]$config.target_type
    $targetArgs = @()
    if ($null -ne $config.args) {
        $targetArgs = @($config.args | ForEach-Object { [string]$_ })
    }

    Write-RunnerLog ("[INFO] Executando elevado: " + $targetPath)

    if ($targetType -eq ".ps1") {
        & powershell.exe -ExecutionPolicy Bypass -NoProfile -NonInteractive -File $targetPath @targetArgs *>&1 |
            Tee-Object -FilePath $script:OutputPath -Append | Out-Null
        $codigoSaida = $LASTEXITCODE
    } elseif ($targetType -eq ".reg") {
        & reg.exe import $targetPath *>&1 |
            Tee-Object -FilePath $script:OutputPath -Append | Out-Null
        $codigoSaida = $LASTEXITCODE
    } else {
        & $targetPath @targetArgs *>&1 |
            Tee-Object -FilePath $script:OutputPath -Append | Out-Null
        $codigoSaida = $LASTEXITCODE
    }

    if ($null -eq $codigoSaida) {
        if ($?) {
            $codigoSaida = 0
        } else {
            $codigoSaida = 1
        }
    }
} catch {
    if (-not $script:OutputPath) {
        $script:OutputPath = Join-Path -Path (Split-Path -Parent $ConfigPath) -ChildPath "runner_output.log"
    }
    if (-not $exitCodePath) {
        $exitCodePath = Join-Path -Path (Split-Path -Parent $ConfigPath) -ChildPath "runner_exit_code.txt"
    }
    Write-RunnerLog ("[ERRO FATAL] " + $_.Exception.Message)
    $codigoSaida = 1
}

Set-Content -LiteralPath $exitCodePath -Value ([string]$codigoSaida) -Encoding UTF8
exit $codigoSaida
""".strip()


def _ps_string(valor):
    return "'" + str(valor).replace("'", "''") + "'"


def _preparar_diretorio_runner(diretorio_raiz):
    runner_dir = os.path.join(diretorio_raiz, ".tmp", "runner")
    os.makedirs(runner_dir, exist_ok=True)
    return runner_dir


def _limpar_runner_antigos(runner_temp_root):
    if not os.path.isdir(runner_temp_root):
        return

    for nome in os.listdir(runner_temp_root):
        if not nome.startswith("lynch_runner_"):
            continue
        _limpar_diretorio_temporario(os.path.join(runner_temp_root, nome))


def _limpar_diretorio_temporario(temp_dir):
    try:
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass


def _formatar_comando(comando):
    return subprocess.list2cmdline(comando)


def _log(logger, mensagem):
    if logger:
        logger(mensagem)
