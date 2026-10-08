from pathlib import Path

from backend.app import create_app


def test_data_root_override_is_used_for_portable_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("ALLEN_DATA_ROOT", str(tmp_path))
    app = create_app()
    assert app.state.db.path == tmp_path / "allen.sqlite3"


def test_distribution_files_define_both_windows_packages():
    root = Path(__file__).resolve().parent.parent
    workflow = (root / ".github/workflows/windows-distribution.yml").read_text(encoding="utf-8")
    build = (root / "distribution/build_windows.ps1").read_text(encoding="utf-8")
    installer = (root / "distribution/installer.iss").read_text(encoding="utf-8")
    launcher = (root / "distribution/allen_launcher.py").read_text(encoding="utf-8")

    assert "Portable-Windows-x64.zip" in build
    assert "Setup-Windows-x64.exe" in build
    assert "portable.flag" in build
    assert "ALLEN_DATA_ROOT" in launcher
    assert "PrivilegesRequired=lowest" in installer
    assert "actions/upload-artifact@v4" in workflow


def test_complete_remover_is_packaged_and_guarded():
    root = Path(__file__).resolve().parent.parent
    build = (root / "distribution/build_windows.ps1").read_text(encoding="utf-8")
    installer = (root / "distribution/installer.iss").read_text(encoding="utf-8")
    remover = (root / "distribution/remove_allen.ps1").read_text(encoding="utf-8")
    launcher = (root / "distribution/Eliminar ALLEN completamente.bat").read_text(encoding="utf-8")

    assert "Eliminar ALLEN completamente.bat" in build
    assert "remove_allen.ps1" in build
    assert "Eliminar ALLEN completamente" in installer
    assert 'Read-Host "Escribe BORRAR para continuar"' in remover
    assert "Stop-Process -Force" in remover
    assert "ALLEN_DATA_ROOT" not in launcher
    assert "remove_allen.ps1" in launcher
