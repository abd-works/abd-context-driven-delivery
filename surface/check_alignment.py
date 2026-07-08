"""CLI entry for surface.md § Satisfy — delegates to Surface API alignment."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_surface_module(surface_dir: Path):
    py_path = surface_dir / f"{surface_dir.name}.py"
    spec = importlib.util.spec_from_file_location(
        f"_surface_align_{surface_dir.name}", py_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {py_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def alignment_errors(surface_dir: Path) -> list[str]:
    surface_dir = surface_dir.resolve()
    mod = _load_surface_module(surface_dir)
    class_name = "".join(
        part.capitalize() for part in surface_dir.name.replace("_", "-").split("-")
    )
    surface = getattr(mod, class_name)(surface_dir)
    return surface.alignment_violations()


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    surface_dir = Path(args[0]).resolve() if args else Path(__file__).resolve().parent
    errors = alignment_errors(surface_dir)
    if errors:
        for err in errors:
            print(f"satisfy FAIL: {err}")
        return 1
    print(f"satisfy OK: type contract aligned — {surface_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
