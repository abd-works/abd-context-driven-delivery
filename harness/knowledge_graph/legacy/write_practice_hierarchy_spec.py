"""First-class CE modules are domain folders, not tests or host apps."""

import sys
from pathlib import Path

from expects import contain, equal, expect

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from write_practice_hierarchy import _ce_folders, _top_level_folders


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("export class Thing {}\n", encoding="utf-8")


with description("CE folders"):
    with it("should keep domain aggregates and drop tests and apps"):
        root = Path(__file__).resolve().parent / ".tmp-ce-folders"
        try:
            _touch(root / "domain" / "customer" / "customer.ts")
            _touch(root / "domain" / "prospect" / "prospect.ts")
            _touch(root / "tests" / "onboard-a-customer" / "sign-up.e2e.ts")
            _touch(root / "apps" / "mid-tier" / "server.ts")
            folders = _ce_folders(root)
            expect(folders).to(contain("domain/customer"))
            expect(folders).to(contain("domain/prospect"))
            expect("tests" in folders).to(equal(False))
            expect("apps" in folders).to(equal(False))
            expect("apps/mid-tier" in folders).to(equal(False))
            expect(_top_level_folders(root)).to(contain("domain"))
            expect("tests" in _top_level_folders(root)).to(equal(False))
            expect("apps" in _top_level_folders(root)).to(equal(False))
        finally:
            import shutil

            shutil.rmtree(root, ignore_errors=True)
