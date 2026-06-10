
from __future__ import annotations

import tempfile
from pathlib import Path

from conftest import PROJECT_ROOT, load_python_module


def test_runner_blocks_third_party_optimizer_folder():
    runner = load_python_module("runner_safety_test", "core/runner.py")
    target = PROJECT_ROOT / "scripts" / "otimizadores" / "WinTool.ps1"

    assert runner._esta_em_terceiros_isolados(str(target), str(PROJECT_ROOT)) is True


def test_runner_allows_windows_tweaks_folder():
    runner = load_python_module("runner_windows_tweaks_test", "core/runner.py")
    target = PROJECT_ROOT / "scripts" / "windows_tweaks" / "script_reduzir_input_lag.ps1"

    assert runner._esta_em_terceiros_isolados(str(target), str(PROJECT_ROOT)) is False
    assert runner._esta_dentro_do_projeto(str(target), str(PROJECT_ROOT)) is True


def test_runner_uses_argument_lists_without_shell_true():
    runner_source = (PROJECT_ROOT / "core" / "runner.py").read_text(encoding="utf-8")

    assert "shell=True" not in runner_source
    assert "subprocess.Popen(" in runner_source
    assert "shell=False" in runner_source


def test_runner_cleanup_removes_lynch_runner_directories():
    runner = load_python_module("runner_cleanup_test", "core/runner.py")

    with tempfile.TemporaryDirectory() as temp_root:
        temp_root_path = Path(temp_root)
        stale_dir = temp_root_path / "lynch_runner_test"
        stale_dir.mkdir()
        (stale_dir / "runner_output.log").write_text("ok", encoding="utf-8")

        ignored_dir = temp_root_path / "unrelated"
        ignored_dir.mkdir()

        runner._limpar_runner_antigos(str(temp_root_path))

        assert not stale_dir.exists()
        assert ignored_dir.exists()
