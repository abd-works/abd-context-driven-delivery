"""Send bytecode for this checkout to one directory before tests import the tree."""
import os
import sys
from pathlib import Path

os.environ["PYTHONPYCACHEPREFIX"] = str(Path(__file__).resolve().parent / ".pycache")
sys.pycache_prefix = os.environ["PYTHONPYCACHEPREFIX"]
