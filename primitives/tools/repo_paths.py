"""Repo category dirs for ``python -m tools`` — this checkout, not another clone."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

CATEGORY_DIRS = ("primitives", "utilities", "context_tools", "context_tools/actions")
_PTH_NAME = "abd_cdd_paths.pth"
_CFG_NAME = "pyvenv.cfg"
_VENV_COMMAND = " -m venv "


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repo_source_paths(root: Path | None = None) -> list[Path]:
    root = (root or repo_root()).resolve()
    return [root] + [root / name for name in CATEGORY_DIRS]


def pythonpath_entries(root: Path | None = None) -> list[str]:
    return [str(path) for path in repo_source_paths(root)]


def _site_packages_dir(venv_dir: Path) -> Path:
    venv_dir = Path(venv_dir)
    for candidate in (
        venv_dir / "Lib" / "site-packages",
        venv_dir / "lib" / "site-packages",
    ):
        if candidate.is_dir():
            return candidate
    path = venv_dir / "Lib" / "site-packages"
    path.mkdir(parents=True, exist_ok=True)
    return path


def venv_pth_entries(venv_dir: Path, root: Path | None = None) -> list[str]:
    """Repo paths relative to ``Lib/site-packages`` for portable ``.pth`` files."""
    site_packages = _site_packages_dir(Path(venv_dir))
    return [
        Path(os.path.relpath(source, site_packages)).as_posix()
        for source in repo_source_paths(root)
    ]


def prepend_sys_path(root: Path | None = None) -> None:
    for entry in reversed(pythonpath_entries(root)):
        if entry not in sys.path:
            sys.path.insert(0, entry)


def write_venv_pth(venv_dir: Path, root: Path | None = None) -> Path:
    """Write ``abd_cdd_paths.pth`` under site-packages so import uses *this* repo."""
    venv_dir = Path(venv_dir)
    path = _site_packages_dir(venv_dir) / _PTH_NAME
    path.write_text("\n".join(venv_pth_entries(venv_dir, root)) + "\n", encoding="utf-8")
    legacy = venv_dir / _PTH_NAME
    if legacy.is_file() and legacy != path:
        legacy.unlink()
    return path


def tools_package_is_from(root: Path | None = None) -> bool:
    import tools

    root = (root or repo_root()).resolve()
    return Path(tools.__file__).resolve().is_relative_to(root)


def venv_python(venv_dir: Path) -> Path:
    venv_dir = Path(venv_dir)
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _read_pyvenv_cfg(venv_dir: Path) -> dict[str, str]:
    path = Path(venv_dir) / _CFG_NAME
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    # utf-8-sig: a hand-edited cfg can carry a BOM, which would hide the first key.
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        key, separator, value = line.partition("=")
        if separator:
            values[key.strip().lower()] = value.strip()
    return values


def _venv_built_for(config: dict[str, str]) -> Path | None:
    """Destination from the ``command`` line — ``pyvenv.cfg`` never quotes its paths."""
    _, separator, tail = config.get("command", "").rpartition(_VENV_COMMAND)
    if not separator:
        return None
    words = [word for word in tail.split() if not word.startswith("-")]
    if not words:
        return None
    return Path(words[-1])


def _same_path(one: Path, other: Path) -> bool:
    return os.path.normcase(str(one.resolve())) == os.path.normcase(str(other.resolve()))


def _interpreter_runs(python: Path) -> bool:
    try:
        completed = subprocess.run(
            [str(python), "-I", "-S", "-c", "pass"],
            capture_output=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0


def venv_problem(venv_dir: Path, *, probe: bool = True) -> str:
    """Why *venv_dir* is unusable where it sits, or ``""`` when it is healthy.

    A venv copied or inherited from another checkout keeps the machine and
    destination it was built for, so its interpreter cannot find a stdlib here.
    """
    venv_dir = Path(venv_dir)
    if not venv_dir.is_dir():
        return f"no venv at {venv_dir}"
    python = venv_python(venv_dir)
    if not python.is_file():
        return f"no interpreter at {python}"
    config = _read_pyvenv_cfg(venv_dir)
    if not config:
        return f"no {_CFG_NAME} at {venv_dir}"
    for key in ("home", "executable"):
        recorded = config.get(key, "")
        if recorded and not Path(recorded).exists():
            return f"{_CFG_NAME} {key} is {recorded}, which is not on this machine"
    built_for = _venv_built_for(config)
    if built_for is not None and not _same_path(built_for, venv_dir):
        return f"{_CFG_NAME} was built for {built_for}, not {venv_dir}"
    if probe and not _interpreter_runs(python):
        return f"{python} does not run"
    return ""


def ensure_venv(root: Path | None = None) -> str:
    """Rebuild ``{root}/.venv`` through ``setup.ps1`` when it cannot serve *root*.

    Returns the problem that was repaired, or ``""`` when nothing was needed.
    """
    root = Path(root or repo_root()).resolve()
    setup = root / "setup.ps1"
    if os.name != "nt" or not setup.is_file():
        return ""
    venv = root / ".venv"
    problem = venv_problem(venv)
    if not problem:
        return ""
    if _same_path(Path(sys.prefix), venv):
        # setup.ps1 deletes the venv; Windows will not let us pull it out from under
        # the interpreter running this call.
        return f"{problem}; run setup.ps1 in {root} — this process runs from that venv"
    try:
        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(setup),
            ],
            cwd=str(root),
            capture_output=True,
            timeout=900,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return f"{problem}; setup.ps1 failed: {error}"
    remaining = venv_problem(venv)
    if remaining:
        return f"{problem}; still broken after setup.ps1: {remaining}"
    return problem
