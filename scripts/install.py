"""Install CDD toolsets by calling harness/installation/installer.py."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    parser = argparse.ArgumentParser(description="Install CDD toolsets into the IDE path.")
    parser.add_argument(
        "--ide",
        default=None,
        help="IDE name: Cursor, VS Code, Kilo, or Claude. Default is the saved install, or Cursor.",
    )
    parser.add_argument("--path", default=None, help="IDE config directory. Default is the saved install path.")
    parser.add_argument(
        "--no-replace",
        action="store_true",
        help="Leave files from the previous install in place.",
    )
    parser.add_argument(
        "--self",
        action="store_true",
        help="Deploy only the Installer toolset (slash /install and /clean, hooks).",
    )
    args = parser.parse_args()
    from harness.installation.installer import Installer

    installer = Installer(ide=args.ide, path=args.path, repo=_REPO)
    if args.self:
        installer.install_self(replace=not args.no_replace)
    else:
        installer.install(replace=not args.no_replace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
