from __future__ import annotations

import ast
import json
import re

from conftest import PROJECT_ROOT


def test_windows_tweaks_powershell_does_not_use_forbidden_aliases():
    offenders = []
    pattern = re.compile(r"(?<!\S)-EA(?!\S)", re.IGNORECASE)

    for path in (PROJECT_ROOT / "scripts" / "windows_tweaks").glob("*.ps1"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            offenders.append(str(path.relative_to(PROJECT_ROOT)))

    assert offenders == []


def test_ui_does_not_use_print_for_operational_logs():
    offenders = []

    for path in (PROJECT_ROOT / "ui").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
                offenders.append((str(path.relative_to(PROJECT_ROOT)), node.lineno))

    assert offenders == []


def test_modal_geometries_respect_minimum_agents_size():
    modais_path = PROJECT_ROOT / "ui" / "modais.py"
    text = modais_path.read_text(encoding="utf-8", errors="replace")
    offenders = []

    for match in re.finditer(r"geometry\([\"'](\d+)x(\d+)", text):
        width = int(match.group(1))
        height = int(match.group(2))
        if width < 560 or height < 440:
            line = text.count("\n", 0, match.start()) + 1
            offenders.append((line, width, height))

    assert offenders == []


def test_otimizadores_has_governance_readme():
    readme = PROJECT_ROOT / "scripts" / "otimizadores" / "README_GOVERNANCA.md"

    assert readme.exists()
    text = readme.read_text(encoding="utf-8")
    assert "Nao integrar arquivos desta pasta diretamente no Hub." in text
    assert "core/runner.py" in text


def test_gitignore_excludes_generated_artifacts():
    gitignore = PROJECT_ROOT / ".gitignore"

    assert gitignore.exists()
    text = gitignore.read_text(encoding="utf-8")
    required_patterns = [
        "__pycache__/",
        "*.py[cod]",
        ".DS_Store",
        "output.log",
        ".tmp/",
        ".env",
        ".env.*",
        "credentials.json",
        "token.json",
        "*.pem",
        "*.pfx",
        "*.p12",
        "*.key",
    ]

    missing = [pattern for pattern in required_patterns if pattern not in text]

    assert missing == []


def test_build_manifest_requires_administrator():
    manifest = PROJECT_ROOT / "packaging" / "LynchBoost.exe.manifest"

    assert manifest.exists()
    text = manifest.read_text(encoding="utf-8")
    assert 'requestedExecutionLevel level="requireAdministrator"' in text
    assert 'uiAccess="false"' in text


def test_pyinstaller_spec_uses_admin_manifest_and_excludes_third_party_optimizers():
    spec = PROJECT_ROOT / "LynchBoost.spec"

    assert spec.exists()
    text = spec.read_text(encoding="utf-8")
    assert 'manifest="packaging/LynchBoost.exe.manifest"' in text
    assert 'Tree("scripts/windows_tweaks", prefix="scripts/windows_tweaks")' in text
    assert 'Tree("scripts/otimizadores"' not in text


def test_edge_modal_exposes_background_reduction_action_supported_by_script():
    menu = PROJECT_ROOT / "ui" / "menu_edge.py"
    script = PROJECT_ROOT / "scripts" / "windows_tweaks" / "script_remover_edge.ps1"

    menu_text = menu.read_text(encoding="utf-8", errors="replace")
    script_text = script.read_text(encoding="utf-8", errors="replace")

    assert "Reduzir Edge em Segundo Plano" in menu_text
    assert '"-ReduceBackground", "-NonInteractive"' in menu_text
    assert "[switch]$ReduceBackground" in script_text
    assert "function ReduceEdgeBackground" in script_text
    assert "BackgroundModeEnabled" in script_text
    assert "StartupBoostEnabled" in script_text


def test_visual_performance_script_preserves_font_smoothing():
    script = PROJECT_ROOT / "scripts" / "windows_tweaks" / "script_desempenho_visual.ps1"

    text = script.read_text(encoding="utf-8", errors="replace")
    required_settings = [
        'FontSmoothing" -Value "2"',
        'FontSmoothingType" -Value 2',
        'FontSmoothingGamma" -Value 1200',
        'FontSmoothingOrientation" -Value 1',
        "SPI_SETFONTSMOOTHING",
    ]

    missing = [setting for setting in required_settings if setting not in text]

    assert missing == []


def test_main_uses_operational_v2_interface():
    main_path = PROJECT_ROOT / "main.py"
    ui_path = PROJECT_ROOT / "ui" / "janela_principal_v2.py"

    main_text = main_path.read_text(encoding="utf-8", errors="replace")
    ui_text = ui_path.read_text(encoding="utf-8", errors="replace")

    assert "from ui.janela_principal_v2 import PCBoosterHub" in main_text
    assert "Painel Operacional" in ui_text
    assert "Modo de execucao" in ui_text
    assert "Execucao individual" in ui_text
    assert "_build_action_catalog" in ui_text
    assert "Plano de execucao" not in ui_text
    assert "Adicionar ao Plano" not in ui_text
    assert "action_plan" not in ui_text
    assert "Referencia tecnica" not in ui_text
    assert "Script associado" not in ui_text
    assert "_action_reference" not in ui_text
    assert '{"name": "Limpar Arquivos Temporarios", "category": "limpeza_armazenamento"}' in ui_text
    assert '{"name": "Esvaziar Lixeira do PC", "category": "limpeza_armazenamento"}' in ui_text
    assert '{"command": "abrir_desfragmentador", "category": "limpeza_armazenamento"}' in ui_text
    assert '{"action": "abrir_menu_dns", "category": "rede_latencia"}' in ui_text
    assert '{"name": "Desinstalar Windows Apps", "category": "debloat_servicos"}' not in ui_text
    assert '{"name": "Gerenciar Plano de Energia", "category": "cpu_energia"}' not in ui_text


def test_windows_app_removal_catalog_and_executor_are_wired_safely():
    catalog_path = PROJECT_ROOT / "dados" / "apps_windows_remocao.json"
    executor_path = PROJECT_ROOT / "scripts" / "windows_tweaks" / "script_remover_apps_windows.ps1"
    menu_path = PROJECT_ROOT / "ui" / "menu_desinstalar_apps_windows.py"
    config_path = PROJECT_ROOT / "config.json"

    assert catalog_path.exists()
    assert executor_path.exists()
    assert menu_path.exists()

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    items = [item for group in catalog.values() for item in group]
    ids = [item["id"] for item in items]

    assert len(ids) == len(set(ids))
    required_ids = {
        "3d_viewer",
        "bing_search",
        "calculator",
        "clipchamp",
        "copilot",
        "internet_explorer",
        "microsoft_store",
        "recall",
        "snipping_tool",
        "windows_terminal",
        "xbox_apps",
        "phone_link",
    }
    external_specials = {"onedrive", "microsoft_edge", "xbox_game_bar"}
    assert required_ids <= set(ids)
    assert external_specials.isdisjoint(set(ids))

    for item in items:
        assert item["tipo"] in {"appx", "feature", "capability"}
        assert "arquivo" not in item

    executor_text = executor_path.read_text(encoding="utf-8", errors="replace")
    assert "Remove-AppxProvisionedPackage -AllUsers -Online" in executor_text
    assert "Remove-AppxPackage -AllUsers" in executor_text
    assert "Remove-WindowsCapability -Online" in executor_text
    assert "Disable-WindowsOptionalFeature -Online -Remove" in executor_text
    assert "[AllowEmptyString()]" in executor_text

    xbox_apps = next(item for item in items if item["id"] == "xbox_apps")
    xbox_selectors = set(xbox_apps["appx_selectors"])
    assert {
        "Microsoft.GamingApp",
        "Microsoft.GamingServices",
        "Microsoft.XboxApp",
        "Microsoft.XboxIdentityProvider",
        "Microsoft.Xbox.TCUI",
    } <= xbox_selectors
    assert set(xbox_apps["services_to_disable"]) == {"GamingServices", "GamingServicesNet"}
    assert {
        "Registry::HKLM\\SYSTEM\\CurrentControlSet\\Services\\GamingServices",
        "Registry::HKLM\\SYSTEM\\CurrentControlSet\\Services\\GamingServicesNet",
    } <= set(xbox_apps["registry_delete_paths"])
    assert "Microsoft.XboxGamingOverlay" not in xbox_selectors
    assert "Microsoft.XboxGameOverlay" not in xbox_selectors

    config = json.loads(config_path.read_text(encoding="utf-8"))
    debloat = next(item for item in config["debloat_servicos"] if item["nome"] == "Desinstalar Windows Apps")
    assert debloat["acao_especial"] == "abrir_menu_desinstalar_apps_windows"


def test_project_owned_files_do_not_expose_local_user_paths():
    offenders = []
    ignored_roots = {
        PROJECT_ROOT / ".git",
        PROJECT_ROOT / "scripts" / "otimizadores",
    }
    checked_suffixes = {".py", ".json", ".md", ".ini", ".bat", ".cmd", ".ps1", ".reg", ".txt", ".yml", ".yaml"}
    forbidden_patterns = [
        "C:" + "\\Users\\Usuario",
        "C:" + "/Users/Usuario",
        "luizfelipe.consultoria20" + "@gmail.com",
    ]

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(root in path.parents for root in ignored_roots):
            continue
        if path.suffix.lower() not in checked_suffixes and path.name != ".gitignore":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in forbidden_patterns:
            if pattern in text:
                offenders.append((str(path.relative_to(PROJECT_ROOT)), pattern))

    assert offenders == []
