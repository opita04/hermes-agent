from pathlib import Path


def test_find_bash_prefers_git_bash_over_wsl_launcher(monkeypatch, tmp_path):
    """On Windows, System32 bash.exe is WSL; local tools need Git Bash."""
    import tools.environments.local as local

    git_root = tmp_path / "Git"
    git_bash = git_root / "bin" / "bash.exe"
    git_bash.parent.mkdir(parents=True)
    git_bash.write_text("", encoding="utf-8")

    monkeypatch.setattr(local, "_IS_WINDOWS", True)
    monkeypatch.setenv("ProgramFiles", str(tmp_path))
    monkeypatch.delenv("ProgramFiles(x86)", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.delenv("HERMES_GIT_BASH_PATH", raising=False)
    monkeypatch.setattr(local.shutil, "which", lambda name: r"C:\WINDOWS\System32\bash.EXE")
    monkeypatch.setattr(local.os.path, "isfile", lambda path: Path(path) == git_bash)

    assert local._find_bash() == str(git_bash)
