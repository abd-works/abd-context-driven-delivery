"""BDD graphQuery rules — CodeQL-appropriate subset.

Skipped (not CodeQL): red-then-green, one-signature-at-a-time, scan-fixture-pair,
usage-order-behaviors, full-surface-coverage, framework-syntax, minimum-green —
process and completeness, not AST. domain-practice-alignment is a connector that
needs the domain model vocabulary, not just this spec file.
"""

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

_GQS = _REPO_ROOT / "harness" / "knowledge_graph" / "model" / "graph_query_spec.py"
_spec = importlib.util.spec_from_file_location("graph_query_spec", _GQS)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
assert_pack_hits = _mod.assert_pack_hits

_PACK = Path(__file__).resolve().parent
_EXAMPLES = Path(__file__).resolve().parents[2] / "examples"

_RULES = {
    "one-assertion-per-test": "more than one assertion",
    "describe-is-subject-not-internal": "SessionLog",
    "state-not-when": "when",
    "observable-behavior": "private attribute",
}


with description("BDD graphQuery rules"):
    with it("should hit each CodeQL-appropriate rule example in one batch"):
        misses = assert_pack_hits(_PACK, _EXAMPLES, "python", _RULES)
        expect(misses).to(equal([]))
