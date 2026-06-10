from __future__ import annotations

import ast
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
