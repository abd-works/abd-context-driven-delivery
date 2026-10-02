"""A code-format build writes .context/bounded-context.md for each context folder."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from harness.transformers.transformers import Transformers
from practices.ddd.model.transformation.ddd_transformer import DddTransformer


with description("DddTransformer"):
    with description("a code-format build"):
        with it("should write bounded-context.md in each context folder"):
            roots = Transformers().transform_sketch(
                "ddd:\n"
                "  Customer | custom\n"
                "    customer\n"
                "    account-credentials\n"
                "  Subscription | custom\n"
                "    cart\n"
            )
            ddd = next(root for root in roots if isinstance(root, DddTransformer))
            files = ddd.render("logical")
            expect(files["domain/customer/.context/bounded-context.md"]).to(
                equal("# Customer | custom")
            )
            expect(files["domain/subscription/.context/bounded-context.md"]).to(
                equal("# Subscription | custom")
            )
            expect(ddd.contexts[0].aggregates[0]._child_folder()).to(equal("domain/customer/customer"))
            expect(ddd.contexts[0].aggregates[1]._child_folder()).to(equal("domain/customer/account-credentials"))
            expect(ddd.contexts[1].aggregates[0]._child_folder()).to(equal("domain/subscription/cart"))
