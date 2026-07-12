"""Entry point — run as: python -m open <command> [args]."""
import importlib.util
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("_open_impl", _HERE / "open.py")
_mod = importlib.util.module_from_spec(_spec)
sys.modules["_open_impl"] = _mod
_spec.loader.exec_module(_mod)

Surface = _mod.Surface
Open = _mod.Open
OpenCli = _mod.OpenCli


def main() -> None:
    args = sys.argv[1:]
    surface_path = _HERE

    if len(args) >= 2 and args[0] == "--surface":
        surface_path = Path(args[1]).resolve()
        args = args[2:]

    surface = Surface(surface_path)
    cli = OpenCli(Open(surface))
    sys.exit(cli.execute(args))


if __name__ == "__main__":
    main()
