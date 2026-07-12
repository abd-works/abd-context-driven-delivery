"""Entry point — run as: python -m capability <command> [args]."""
import importlib.util
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("_capability_impl", _HERE / "capability.py")
_mod = importlib.util.module_from_spec(_spec)
sys.modules["_capability_impl"] = _mod
_spec.loader.exec_module(_mod)

Capability = _mod.Capability
CapabilityCli = _mod.CapabilityCli


def main() -> None:
    args = sys.argv[1:]
    cap_path = _HERE

    if len(args) >= 2 and args[0] == "--capability":
        cap_path = Path(args[1]).resolve()
        args = args[2:]

    capability = Capability(cap_path)
    cli = CapabilityCli(capability)
    sys.exit(cli.execute(args))


if __name__ == "__main__":
    main()
