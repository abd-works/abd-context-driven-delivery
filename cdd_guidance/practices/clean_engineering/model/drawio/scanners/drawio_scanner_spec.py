"""A Draw.io layout scanner: which files it reads, and what the whole set of scanners reports."""
import tempfile
from pathlib import Path

from expects import be_false, be_true, contain, equal, expect
from mamba import before, description, it, context

from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner
from cdd_guidance.practices.clean_engineering.model.drawio.scanners.prefer_short_routes_scanner import (
    PreferShortRoutesScanner,
)

_FAR_APART = """\
<mxfile host="test">
  <diagram name="Page">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" vertex="1" parent="1" value="&lt;b&gt;Order&lt;/b&gt;">
          <mxGeometry x="0" y="0" width="200" height="80" as="geometry"/>
        </mxCell>
        <mxCell id="3" vertex="1" parent="1" value="&lt;b&gt;Customer&lt;/b&gt;">
          <mxGeometry x="2000" y="0" width="200" height="80" as="geometry"/>
        </mxCell>
        <mxCell id="4" edge="1" parent="1" source="2" target="3" style="endArrow=open;">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


_TWO_EDGES_TO_ONE_POINT = """\
<mxfile host="test">
  <diagram name="Page">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" vertex="1" parent="1" value="&lt;b&gt;Payment&lt;/b&gt;">
          <mxGeometry x="300" y="60" width="200" height="80" as="geometry"/>
        </mxCell>
        <mxCell id="3" vertex="1" parent="1" value="&lt;b&gt;CardPayment&lt;/b&gt;">
          <mxGeometry x="60" y="260" width="200" height="80" as="geometry"/>
        </mxCell>
        <mxCell id="4" vertex="1" parent="1" value="&lt;b&gt;CashPayment&lt;/b&gt;">
          <mxGeometry x="540" y="260" width="200" height="80" as="geometry"/>
        </mxCell>
        <mxCell id="5" edge="1" parent="1" source="3" target="2" style="edgeStyle=orthogonalEdgeStyle;{head}exitX=0.5;exitY=0;entryX=0.5;entryY=1;">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="160" y="210"/><mxPoint x="400" y="210"/></Array></mxGeometry>
        </mxCell>
        <mxCell id="6" edge="1" parent="1" source="4" target="2" style="edgeStyle=orthogonalEdgeStyle;{head}exitX=0.5;exitY=0;entryX=0.5;entryY=1;">
          <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="640" y="210"/><mxPoint x="400" y="210"/></Array></mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

_INHERITANCE_HEAD = "endArrow=block;endSize=16;endFill=0;"
_ASSOCIATION_HEAD = "endArrow=open;endSize=12;"


def _rules_reported(head: str) -> list:
    path = Path(tempfile.mkdtemp()) / "payments.drawio"
    path.write_text(_TWO_EDGES_TO_ONE_POINT.replace("{head}", head), encoding="utf-8")
    report = DrawioScanner(scan_root=path.parent).run_report([str(path)])
    return [item["rule"] for item in report["violations"] if item["rule"] in ("distinct-anchor-points", "edges-do-not-overlap-edges")]


def _diagram_in_examples() -> Path:
    folder = Path(tempfile.mkdtemp()) / "examples"
    folder.mkdir()
    path = folder / "model.drawio"
    path.write_text(_FAR_APART, encoding="utf-8")
    return path


with description("a Draw.io layout scanner"):
    with context("with a diagram inside a folder a workspace scan skips"):
        with before.each:
            self.path = _diagram_in_examples()

        with it("should read the diagram when the caller named it"):
            scanner = DrawioScanner(explicit_paths=[self.path])
            expect(scanner.is_skipped_path(self.path)).to(be_false)

        with it("should skip the diagram for a scanner whose caller named nothing"):
            DrawioScanner(explicit_paths=[self.path])
            expect(DrawioScanner().is_skipped_path(self.path)).to(be_true)

    # A scan reads every scanner's rules over the diagram, so each context scans once, before its examples read the report.
    with context("that prefers short routes, given two related classes far apart"):
        with before.all:
            path = _diagram_in_examples()
            self.violations = PreferShortRoutesScanner(explicit_paths=[path]).scan(path.parent, [path])

        with it("should report the gap between them"):
            expect(self.violations[0].message).to(contain("endpoint gap"))

        with it("should name the page and both classes"):
            expect(self.violations[0].message).to(contain("[Page] Order → Customer"))

    with context("that reports on every rule for named paths"):
        with before.all:
            path = _diagram_in_examples()
            self.report = DrawioScanner(scan_root=path.parent).run_report([str(path)])

        with it("should keep the violations of every rule when no rule is named"):
            expect([item["rule"] for item in self.report["violations"]]).to(contain("prefer-short-routes"))

        with it("should not call the diagram clean"):
            expect(self.report["ok"]).to(equal(False))

    with context("with two subclasses joined into one shared line to their base"):
        with before.all:
            self.rules = _rules_reported(_INHERITANCE_HEAD)

        with it("should report neither a shared anchor nor an overlap"):
            expect(self.rules).to(equal([]))

    with context("with two associations that end at one point and share the last line"):
        with before.all:
            self.rules = _rules_reported(_ASSOCIATION_HEAD)

        with it("should report the shared anchor and the overlap"):
            expect(sorted(self.rules)).to(equal(["distinct-anchor-points", "edges-do-not-overlap-edges"]))

    with context("that reports on named paths with no scan root"):
        with before.all:
            path = _diagram_in_examples()
            self.report = DrawioScanner().run_report([str(path)])

        with it("should scan the folder the paths share"):
            expect([item["rule"] for item in self.report["violations"]]).to(contain("prefer-short-routes"))
