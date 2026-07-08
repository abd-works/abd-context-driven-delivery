"""Entry point — run as: python cdd-capability/__main__.py <command> [args]."""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import importlib.util as _ilu

_spec = _ilu.spec_from_file_location("cdd_capability", _HERE / "cdd-capability.py")
_mod = _ilu.module_from_spec(_spec)
sys.modules["cdd_capability"] = _mod  # required for @dataclass resolution with hyphenated name
_spec.loader.exec_module(_mod)

Capability = _mod.Capability
CapabilityCli = _mod.CapabilityCli


def main() -> None:
    args = sys.argv[1:]
    cap_path = _HERE  # default: operate on cdd-capability itself

    # --capability <path> lets you target any capability with this CLI.
    if len(args) >= 2 and args[0] == "--capability":
        cap_path = Path(args[1]).resolve()
        args = args[2:]

    capability = Capability(cap_path)
    cli = CapabilityCli(capability)
    sys.exit(cli.execute(args))


if __name__ == "__main__":
    main()
