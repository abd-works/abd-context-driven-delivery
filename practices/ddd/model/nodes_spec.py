"""BDD spec for DDD practice model nodes."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from practices.ddd.model import ddd_class_kind


with description("DDD model nodes"):
    with it("should classify tactical stereotypes from decorated class names"):
        expect(ddd_class_kind("**ShoppingCart** <<Aggregate Root>> <<Entity>>")).to(
            equal("EntityRoot")
        )
        expect(ddd_class_kind("**CartItem** <<Value Object>>")).to(equal("ValueObject"))
        expect(ddd_class_kind("**ShoppingCartRepository** <<Repository>>")).to(
            equal("Repository")
        )

