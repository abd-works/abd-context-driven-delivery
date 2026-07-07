"""Entry point for `python -m enforce.scanners`. Delegates to scanner.main."""
from enforce.scanners.scanners import main
import sys

if __name__ == "__main__":
    sys.exit(main())
