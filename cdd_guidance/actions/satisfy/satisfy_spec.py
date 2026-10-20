"""BDD spec — Satisfy action."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.installation.bootstrap import ensure_import_path

ensure_import_path(_REPO_ROOT)

from expects import contain, expect
from mamba import description, it

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from satisfy.satisfy import Satisfy


with description("satisfy on practice guidance"):
    with it("should return validate rules and generate-fixes instructions without error"):
        practice = CleanEngineering(fidelity="code", format="python")
        text = Satisfy().satisfy([practice])
        expect(text).to(contain("Validate"))
        expect(text).to(contain("vocabulary-traces-to-source"))
        expect(text).to(contain("generate_fixes_from_validate"))
        expect(text).to(contain("Fixes"))
