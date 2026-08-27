"""BDD spec for DDD scanners — mechanical rules from pml-domain-tests mistakes."""

import sys
import tempfile
from pathlib import Path

from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, expect

from context_tools.bdd.spec_helpers import expect_scan_fails, expect_scan_passes
from scan import Scan, ScannerCollection

_DDD = _REPO / "context_tools" / "ddd"
_SCANNERS = _DDD / "scanners"

_SCREEN_RULE = "screen-interface-not-a-domain-object"
_PRIVATE_RULE = "private-method-naming"
_STEREOTYPE_RULE = "building-blocks-fidelity-requires-tactical-stereotype"
_FLACCID_RULE = "flaccid-data-object-no-behavior"
_ORPHAN_RULE = "no-orphaned-objects"


class _DddScan(Scan):
    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection(module_dir=_DDD, root_path=_SCANNERS)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


_SCREEN_FAULTY = """\
export interface SelectSim {
  open(): Promise<void>
  isShowing(): Promise<boolean>
  selectEsim(): Promise<void>
}
"""

_SCREEN_OPEN_ONLY = """\
export interface PayNow {
  open(): Promise<void>
  confirmPayment(): Promise<void>
  isSuccessShown(): Promise<boolean>
}
"""

_SCREEN_CLEAN = """\
export interface Cart {
  selectSim(simType: SimType): void
  checkout(): Order
}
"""

_PRIVATE_FAULTY = """\
<mxfile host="test">
  <diagram name="Page">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" vertex="1" parent="1" value="+ deriveOnboardingStep(): OnboardingStep"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

_PRIVATE_CLEAN = """\
<mxfile host="test">
  <diagram name="Page">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" vertex="1" parent="1" value="- _deriveOnboardingStep(): OnboardingStep"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

_STEREOTYPE_FAULTY = """\
fidelity: building_blocks

Catalog
  Plan
    members: Feature; PlanFilter
    repo: PlanRepository
  SelectedPlan
"""

_STEREOTYPE_CLEAN = """\
fidelity: building_blocks

Catalog
  Plan <<Aggregate Root>> <<Entity>>
    members: Feature <<Value Object>>; PlanFilter <<Value Object>>
    repo: PlanRepository <<Repository>>
  SelectedPlan <<Value Object>>
"""

_FLACCID_FAULTY = """\
export interface Cart {
  id: string
  bundle?: Plan
  msisdn?: string
}
"""

_FLACCID_CLEAN = """\
export interface Cart {
  id: string
  bundle?: Plan
  selectPlan(plan: Plan): void
  checkout(): Order
}
"""

_ORPHAN_FAULTY = """\
<mxfile host="test">
  <diagram name="Page">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="cart" vertex="1" parent="1" value="Cart &lt;&lt;Entity&gt;&gt;"/>
        <mxCell id="item" vertex="1" parent="1" value="Item &lt;&lt;Entity&gt;&gt;"/>
        <mxCell id="creds" vertex="1" parent="1" value="Credentials &lt;&lt;Value Object&gt;&gt;"/>
        <mxCell id="e1" edge="1" parent="1" source="cart" target="item"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

_ORPHAN_CLEAN = """\
<mxfile host="test">
  <diagram name="Page">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="cart" vertex="1" parent="1" value="Cart &lt;&lt;Entity&gt;&gt;"/>
        <mxCell id="item" vertex="1" parent="1" value="Item &lt;&lt;Entity&gt;&gt;"/>
        <mxCell id="creds" vertex="1" parent="1" value="Credentials &lt;&lt;Value Object&gt;&gt;"/>
        <mxCell id="e1" edge="1" parent="1" source="cart" target="item"/>
        <mxCell id="e2" edge="1" parent="1" source="cart" target="creds"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


with description("DDD scanner discovery"):
    with it("should discover the mechanical DDD rule slugs"):
        discovered = ScannerCollection(_DDD, _SCANNERS).discover()
        for slug in (
            _SCREEN_RULE,
            _PRIVATE_RULE,
            _STEREOTYPE_RULE,
            _FLACCID_RULE,
            _ORPHAN_RULE,
        ):
            expect(slug in discovered).to(be_true)


with description("a TypeScript domain file under screen-interface-not-a-domain-object"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that models a screen driver with open and isShowing"):
        with before.each:
            self.path = self.root / "select-sim.ts"
            _write(self.path, _SCREEN_FAULTY)

        with it("should fail the scan"):
            expect_scan_fails(_DddScan(), self.path, rule=_SCREEN_RULE, root=self.root)

    with context("that models a screen driver with open and a shown-state query"):
        with before.each:
            self.path = self.root / "pay-now.ts"
            _write(self.path, _SCREEN_OPEN_ONLY)

        with it("should fail the scan"):
            expect_scan_fails(_DddScan(), self.path, rule=_SCREEN_RULE, root=self.root)

    with context("that keeps screen verbs off the domain object"):
        with before.each:
            self.path = self.root / "cart.ts"
            _write(self.path, _SCREEN_CLEAN)

        with it("should pass the scan"):
            expect_scan_passes(_DddScan(), self.path, rule=_SCREEN_RULE, root=self.root)


with description("a class diagram under private-method-naming"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that shows a derive helper as a public + operation"):
        with before.each:
            self.path = self.root / "model.drawio"
            _write(self.path, _PRIVATE_FAULTY)

        with it("should fail the scan"):
            expect_scan_fails(_DddScan(), self.path, rule=_PRIVATE_RULE, root=self.root)

    with context("that marks the derive helper private with an underscore"):
        with before.each:
            self.path = self.root / "model.drawio"
            _write(self.path, _PRIVATE_CLEAN)

        with it("should pass the scan"):
            expect_scan_passes(_DddScan(), self.path, rule=_PRIVATE_RULE, root=self.root)


with description("a building_blocks sketch under tactical stereotype tags"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that lists bare class names"):
        with before.each:
            self.path = self.root / "cdd-sketch.md"
            _write(self.path, _STEREOTYPE_FAULTY)

        with it("should fail the scan"):
            expect_scan_fails(
                _DddScan(), self.path, rule=_STEREOTYPE_RULE, root=self.root
            )

    with context("that tags every class with a DDD stereotype"):
        with before.each:
            self.path = self.root / "cdd-sketch.md"
            _write(self.path, _STEREOTYPE_CLEAN)

        with it("should pass the scan"):
            expect_scan_passes(
                _DddScan(), self.path, rule=_STEREOTYPE_RULE, root=self.root
            )


with description("a TypeScript domain type under flaccid-data-object-no-behavior"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that exposes only properties"):
        with before.each:
            self.path = self.root / "cart.ts"
            _write(self.path, _FLACCID_FAULTY)

        with it("should fail the scan"):
            expect_scan_fails(_DddScan(), self.path, rule=_FLACCID_RULE, root=self.root)

    with context("that owns behavior methods"):
        with before.each:
            self.path = self.root / "cart.ts"
            _write(self.path, _FLACCID_CLEAN)

        with it("should pass the scan"):
            expect_scan_passes(_DddScan(), self.path, rule=_FLACCID_RULE, root=self.root)


with description("a class diagram under no-orphaned-objects"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that leaves a value object unconnected"):
        with before.each:
            self.path = self.root / "domain-model.drawio"
            _write(self.path, _ORPHAN_FAULTY)

        with it("should fail the scan"):
            expect_scan_fails(_DddScan(), self.path, rule=_ORPHAN_RULE, root=self.root)

    with context("that connects every domain object"):
        with before.each:
            self.path = self.root / "domain-model.drawio"
            _write(self.path, _ORPHAN_CLEAN)

        with it("should pass the scan"):
            expect_scan_passes(_DddScan(), self.path, rule=_ORPHAN_RULE, root=self.root)
