"""Install CDD toolsets by calling installation/installer.py."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    parser = argparse.ArgumentParser(description="Install CDD toolsets into the IDE path.")
    parser.add_argument("--ide", default=None, help="IDE name. Default is the saved install, or Cursor.")
    parser.add_argument("--path", default=None, help="IDE config directory. Default is the saved install path.")
    parser.add_argument(
        "--no-replace",
        action="store_true",
        help="Leave files from the previous install in place.",
    )
    args = parser.parse_args()
    from installation.installer import Installer

    Installer(ide=args.ide, path=args.path, repo=_REPO).install(replace=not args.no_replace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
