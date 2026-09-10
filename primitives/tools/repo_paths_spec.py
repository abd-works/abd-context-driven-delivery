"""A venv only serves the checkout it was built for, on this machine."""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_empty, contain, equal, expect
from mamba import context, description, it

from tools.repo_paths import _same_path, ensure_venv, venv_problem, venv_python

_THIS_MACHINE = str(Path(sys.base_prefix))
_ABSENT_MACHINE = r"C:\Users\jeffa\AppData\Local\Programs\Python\Python312"
_OTHER_WORKTREE = r"C:\dev\abd-cdd-better-context-tool-beha\.venv"


def _scratch() -> Path:
    return Path(tempfile.mkdtemp(prefix="venv_health_"))


def _fake_venv(
    root: Path,
    *,
    home: str = _THIS_MACHINE,
    built_for: str = "",
    with_cfg: bool = True,
    with_python: bool = True,
    encoding: str = "utf-8",
) -> Path:
    venv = root / ".venv"
    python = venv_python(venv)
    python.parent.mkdir(parents=True, exist_ok=True)
    if with_python:
        python.write_bytes(b"not a real interpreter")
    creator = str(Path(home) / "python.exe")
    if with_cfg:
        (venv / "pyvenv.cfg").write_text(
            "\n".join(
                [
                    f"home = {home}",
                    "include-system-site-packages = false",
                    "version = 3.12.10",
                    f"executable = {creator}",
                    f"command = {creator} -m venv {built_for or venv}",
                ]
            )
            + "\n",
            encoding=encoding,
        )
    return venv


with description("a venv that is asked to serve this checkout"):
    with context("when it was built here by a Python that is still installed"):
        with it("should report no problem"):
            root = _scratch()
            venv = _fake_venv(root)
            expect(venv_problem(venv, probe=False)).to(be_empty)
            shutil.rmtree(root, ignore_errors=True)

        with it("should accept a creator that is itself a venv interpreter"):
            root = _scratch()
            venv = _fake_venv(root)
            cfg = venv / "pyvenv.cfg"
            cfg.write_text(
                cfg.read_text(encoding="utf-8").replace(
                    f"executable = {Path(_THIS_MACHINE) / 'python.exe'}",
                    f"executable = {_REPO_ROOT / '.venv' / 'Scripts' / 'python.exe'}",
                ),
                encoding="utf-8",
            )
            expect(venv_problem(venv, probe=False)).to(be_empty)
            shutil.rmtree(root, ignore_errors=True)

    with context("when pyvenv.cfg names another machine's Python"):
        with it("should report the home that is not on this machine"):
            root = _scratch()
            venv = _fake_venv(root, home=_ABSENT_MACHINE)
            expect(venv_problem(venv, probe=False)).to(contain(_ABSENT_MACHINE))
            expect(venv_problem(venv, probe=False)).to(contain("not on this machine"))
            shutil.rmtree(root, ignore_errors=True)

        with it("should still read home when the cfg carries a BOM"):
            root = _scratch()
            venv = _fake_venv(root, home=_ABSENT_MACHINE, encoding="utf-8-sig")
            expect(venv_problem(venv, probe=False)).to(contain("home"))
            shutil.rmtree(root, ignore_errors=True)

    with context("when pyvenv.cfg was built for another worktree"):
        with it("should report the destination it was built for"):
            root = _scratch()
            venv = _fake_venv(root, built_for=_OTHER_WORKTREE)
            problem = venv_problem(venv, probe=False)
            expect(problem).to(contain(_OTHER_WORKTREE))
            expect(problem).to(contain(str(venv)))
            shutil.rmtree(root, ignore_errors=True)

        with it("should ignore venv creation flags when reading the destination"):
            root = _scratch()
            venv = _fake_venv(root)
            cfg = venv / "pyvenv.cfg"
            cfg.write_text(
                cfg.read_text(encoding="utf-8").replace("-m venv ", "-m venv --clear "),
                encoding="utf-8",
            )
            expect(venv_problem(venv, probe=False)).to(be_empty)
            shutil.rmtree(root, ignore_errors=True)

    with context("when the venv is incomplete"):
        with it("should report a missing venv directory"):
            root = _scratch()
            expect(venv_problem(root / ".venv", probe=False)).to(contain("no venv at"))
            shutil.rmtree(root, ignore_errors=True)

        with it("should report a missing interpreter"):
            root = _scratch()
            venv = _fake_venv(root, with_python=False)
            expect(venv_problem(venv, probe=False)).to(contain("no interpreter at"))
            shutil.rmtree(root, ignore_errors=True)

        with it("should report a missing pyvenv.cfg"):
            root = _scratch()
            venv = _fake_venv(root, with_cfg=False)
            expect(venv_problem(venv, probe=False)).to(contain("no pyvenv.cfg at"))
            shutil.rmtree(root, ignore_errors=True)

    with context("when the interpreter is present but cannot run"):
        with it("should report that it does not run"):
            root = _scratch()
            venv = _fake_venv(root)
            expect(venv_problem(venv)).to(contain("does not run"))
            shutil.rmtree(root, ignore_errors=True)

    with context("when it is this checkout's own venv"):
        with it("should run and report no problem"):
            expect(venv_problem(_REPO_ROOT / ".venv")).to(be_empty)


with description("a checkout that needs a working venv"):
    with context("when its venv already serves it"):
        with it("should do nothing for this checkout"):
            expect(ensure_venv(_REPO_ROOT)).to(equal(""))

    with context("when the checkout has no setup.ps1 to build with"):
        with it("should leave the checkout alone"):
            root = _scratch()
            expect(ensure_venv(root)).to(equal(""))
            expect((root / ".venv").exists()).to(equal(False))
            shutil.rmtree(root, ignore_errors=True)

    with context("when the broken venv is the one running this call"):
        with it("should recognise that venv so setup.ps1 is never asked to delete it"):
            expect(_same_path(Path(sys.prefix), _REPO_ROOT / ".venv")).to(equal(True))

    with context("when setup.ps1 does not repair the venv"):
        with it("should report what is still wrong rather than claim a repair"):
            root = _scratch()
            (root / "setup.ps1").write_text("exit 0\n", encoding="utf-8")
            _fake_venv(root, built_for=_OTHER_WORKTREE)
            note = ensure_venv(root)
            expect(note).to(contain("still broken after setup.ps1"))
            shutil.rmtree(root, ignore_errors=True)
