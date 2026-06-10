from __future__ import annotations

import ast
import json

from conftest import PROJECT_ROOT, load_python_module


def _config_items():
    data = json.loads((PROJECT_ROOT / "config.json").read_text(encoding="utf-8"))
    return [item for category_items in data.values() for item in category_items]


def _ui_routed_actions():
    tree = ast.parse((PROJECT_ROOT / "ui" / "janela_principal.py").read_text(encoding="utf-8"))
    actions = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        if not isinstance(node.left, ast.Name) or node.left.id != "especial":
            continue
        if len(node.comparators) != 1:
            continue

        comparator = node.comparators[0]
        if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
            actions.add(comparator.value)

    return actions


def test_config_does_not_execute_files_directly():
    offenders = [item["nome"] for item in _config_items() if "arquivo" in item]

    assert offenders == []


def test_all_config_items_have_action_special():
    offenders = [item["nome"] for item in _config_items() if not item.get("acao_especial")]

    assert offenders == []


def test_all_config_actions_are_registered_in_script_registry_or_ui_router():
    acoes_script = load_python_module("acoes_script_router_test", "core/acoes_script.py")
    config_actions = {item["acao_especial"] for item in _config_items()}
    registered_actions = set(acoes_script.ACOES_SCRIPT) | _ui_routed_actions()

    assert config_actions - registered_actions == set()


def test_all_config_script_actions_are_registered():
    acoes_script = load_python_module("acoes_script_test", "core/acoes_script.py")
    registered = set(acoes_script.ACOES_SCRIPT)
    config_actions = {
        item["acao_especial"]
        for item in _config_items()
        if item.get("acao_especial", "").startswith("executar_")
    }

    assert config_actions - registered == set()
    assert registered - config_actions == set()


def test_all_config_actions_have_valid_risk_classification():
    riscos = load_python_module("riscos_config_test", "core/riscos.py")
    config_actions = {item["acao_especial"] for item in _config_items()}
    risk_actions = set(riscos.RISCOS_ACOES)
    invalid_risks = {
        action: risk
        for action, risk in riscos.RISCOS_ACOES.items()
        if risk not in riscos.RISCOS_VALIDOS
    }

    assert config_actions - risk_actions == set()
    assert risk_actions - config_actions == set()
    assert invalid_risks == {}
    assert set(riscos.RISCOS_ACOES.values()) == riscos.RISCOS_VALIDOS


def test_registered_script_actions_expose_risk_metadata():
    acoes_script = load_python_module("acoes_script_risk_test", "core/acoes_script.py")
    riscos = load_python_module("riscos_script_test", "core/riscos.py")
    mismatches = {}

    for action, metadata in acoes_script.ACOES_SCRIPT.items():
        if metadata.get("risco") != riscos.RISCOS_ACOES[action]:
            mismatches[action] = metadata.get("risco")

    assert mismatches == {}


def test_registered_script_paths_exist_and_stay_in_windows_tweaks():
    acoes_script = load_python_module("acoes_script_paths_test", "core/acoes_script.py")
    missing = []
    outside_windows_tweaks = []

    for action, metadata in acoes_script.ACOES_SCRIPT.items():
        relative_path = metadata["arquivo"]
        script_path = PROJECT_ROOT / relative_path
        if not script_path.exists():
            missing.append((action, relative_path))
        if not relative_path.replace("\\", "/").startswith("scripts/windows_tweaks/"):
            outside_windows_tweaks.append((action, relative_path))

    assert missing == []
    assert outside_windows_tweaks == []


def test_removed_legacy_scripts_are_not_referenced():
    legacy_names = {
        "script_fullscreen_fix.reg",
        "script_game_optimizations.reg",
        "script_otimizar_latencia_global.bat",
    }
    searchable_paths = [
        PROJECT_ROOT / "config.json",
        *list((PROJECT_ROOT / "core").glob("*.py")),
        *list((PROJECT_ROOT / "ui").glob("*.py")),
    ]
    references = []

    for path in searchable_paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for legacy_name in legacy_names:
            if legacy_name in text:
                references.append((str(path.relative_to(PROJECT_ROOT)), legacy_name))

    assert references == []
    assert [name for name in legacy_names if (PROJECT_ROOT / "scripts" / "windows_tweaks" / name).exists()] == []
