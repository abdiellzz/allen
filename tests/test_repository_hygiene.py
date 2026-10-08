from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_obsolete_root_launchers_are_not_tracked():
    obsolete = [
        "index.html",
        "install_allen.bat",
        "install_allen.ps1",
        "start_allen.bat",
        "start_local_ai.py",
    ]
    for relative in obsolete:
        assert not (ROOT / relative).exists(), f"obsolete file returned: {relative}"


def test_private_license_material_is_not_tracked():
    assert not (ROOT / "license_private_key.pem").exists()
    tracked_license_files = [
        path for path in ROOT.rglob("*.license")
        if ".venv" not in path.parts and "build" not in path.parts and "dist" not in path.parts
    ]
    assert tracked_license_files == []


def test_required_documentation_exists():
    required = [
        "docs/INDEX.md",
        "docs/INSTALLATION.md",
        "docs/USAGE_GUIDE.md",
        "docs/DEVELOPMENT.md",
        "docs/ARCHITECTURE.md",
        "docs/LICENSING.md",
        "docs/OPERATIONS.md",
        "docs/TROUBLESHOOTING.md",
        "docs/RELEASE_PROCESS.md",
        "docs/WEB_LANDING.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
    ]
    for relative in required:
        assert (ROOT / relative).is_file(), f"missing documentation: {relative}"


def test_current_docs_do_not_reference_removed_launchers():
    removed = ("start_allen.bat", "install_allen.bat", "install_allen.ps1", "start_local_ai.py")
    files = [ROOT / "README.md", ROOT / "SECURITY.md", ROOT / "server.py"]
    files += [
        path for path in (ROOT / "docs").glob("*.md")
        if path.name not in {"RELEASE_1.0.0.md"}
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for name in removed:
            assert name not in text, f"{path.relative_to(ROOT)} references removed {name}"


def test_public_and_local_app_are_separate():
    assert (ROOT / "public" / "index.html").is_file()
    assert (ROOT / "frontend" / "index.html").is_file()
    assert (ROOT / "vercel.json").is_file()


def test_source_tree_contains_no_private_key_material():
    roots=[ROOT/"backend",ROOT/"tools",ROOT/"distribution",ROOT/"config"]
    forbidden=(
        "-----BEGIN PRIVATE KEY-----",
        "-----BEGIN ENCRYPTED PRIVATE KEY-----",
        "github_pat_",
        "ghp_",
    )
    for base in roots:
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py",".json",".txt",".md",".yml",".yaml",".pem"}:
                continue
            text=path.read_text(encoding="utf-8",errors="ignore")
            for marker in forbidden:
                assert marker not in text, f"possible secret material in {path.relative_to(ROOT)}"
