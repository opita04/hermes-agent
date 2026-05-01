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


def test_windows_local_environment_converts_git_bash_cwd_for_subprocess(monkeypatch):
    """Windows subprocess cwd needs a Windows path even when Bash accepts /c/."""
    import tools.environments.local as local

    captured = {}

    class FakeProc:
        returncode = 0
        stdin = None

        def __init__(self):
            self.stdout = []

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

    def fake_popen(*args, **kwargs):
        captured["cwd"] = kwargs.get("cwd")
        return FakeProc()

    monkeypatch.setattr(local, "_IS_WINDOWS", True)
    monkeypatch.setattr(local, "_find_bash", lambda: r"C:\Program Files\Git\bin\bash.exe")
    monkeypatch.setattr(local.subprocess, "Popen", fake_popen)

    env = local.LocalEnvironment(cwd=r"C:\Users\Jaime", timeout=5)
    env.execute("pwd", cwd="/c/AI/Projects/website-factory", timeout=5)

    assert captured["cwd"] == r"C:\AI\Projects\website-factory"
