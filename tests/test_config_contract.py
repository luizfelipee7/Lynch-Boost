from __future__ import annotations

import json

from conftest import PROJECT_ROOT, load_python_module


def _config_items():
    data = json.loads((PROJECT_ROOT / "config.json").read_text(encoding="utf-8"))
    return [item for category_items in data.values() for item in category_items]


def test_config_does_not_execute_files_directly():
    offenders = [item["nome"] for item in _config_items() if "arquivo" in item]

    assert offenders == []


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
