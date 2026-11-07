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

    with context("that prefers short routes, given two related classes far apart"):
        with before.each:
            path = _diagram_in_examples()
            self.violations = PreferShortRoutesScanner(explicit_paths=[path]).scan(path.parent, [path])

        with it("should report the gap between them"):
            expect(self.violations[0].message).to(contain("endpoint gap"))

        with it("should name the page and both classes"):
            expect(self.violations[0].message).to(contain("[Page] Order → Customer"))

    with context("that reports on every rule for named paths"):
        with before.each:
            path = _diagram_in_examples()
            self.report = DrawioScanner(scan_root=path.parent).run_report([str(path)])

        with it("should keep the violations of every rule when no rule is named"):
            expect([item["rule"] for item in self.report["violations"]]).to(contain("prefer-short-routes"))

        with it("should not call the diagram clean"):
            expect(self.report["ok"]).to(equal(False))

    with context("that reports on named paths with no scan root"):
        with before.each:
            path = _diagram_in_examples()
            self.report = DrawioScanner().run_report([str(path)])

        with it("should scan the folder the paths share"):
            expect([item["rule"] for item in self.report["violations"]]).to(contain("prefer-short-routes"))
