"""BDD: stereotype-above-class-name — <<Stereotype>> is above the name, not inside <b>."""
import sys
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

_HERE = Path(__file__).resolve().parent
_REPO = Path(__file__).resolve().parents[5]
for _p in (_REPO, _REPO / "tools", _REPO / "practices"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
sys.path.insert(0, str(_HERE))

from stereotype_above_class_name_scanner import (  # noqa: E402
    StereotypeAboveClassNameScanner,
)
from practices.clean_engineering.model.drawio.diagram_node import DrawIOClass

_FAULTY = """\
<mxfile host="test">
  <diagram name="Page">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" vertex="1" parent="1" value="&lt;b&gt;Prospect &amp;lt;&amp;lt;Aggregate Root&amp;gt;&amp;gt;&lt;/b&gt;">
          <mxGeometry x="40" y="40" width="200" height="80" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

_CLEAN = """\
<mxfile host="test">
  <diagram name="Page">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" vertex="1" parent="1" value="&lt;i&gt;&amp;lt;&amp;lt;Aggregate Root&amp;gt;&amp;gt;&lt;/i&gt;&lt;br/&gt;&lt;b&gt;Prospect&lt;/b&gt;">
          <mxGeometry x="40" y="40" width="200" height="80" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


class _ScannerExample(StereotypeAboveClassNameScanner):
    def scan_xml(self, xml: str):
        tmp = Path(tempfile.mkdtemp())
        path = tmp / "model.drawio"
        path.write_text(xml, encoding="utf-8")
        files = self.collect_drawio_files(tmp)
        return self.scan(tmp, files)


with description("stereotype-above-class-name scanner"):
    with context("a class title that puts the stereotype inside the bold name"):
        with it("should report a violation"):
            violations = _ScannerExample("stereotype-above-class-name").scan_xml(_FAULTY)
            expect(len(violations) > 0).to(equal(True))

    with context("a class title with the stereotype on its own italic line above the name"):
        with it("should produce no violations"):
            violations = _ScannerExample("stereotype-above-class-name").scan_xml(_CLEAN)
            expect(violations).to(equal([]))

    with context("HTML emitted for a class whose name still carries tactical tags"):
        with before.each:
            self.html = DrawIOClass(
                name="Catalog <<Aggregate Root>> <<Entity>>", sequential_order=1
            ).html()

        with it("should include the Aggregate Root stereotype"):
            expect("&lt;&lt;Aggregate Root&gt;&gt;" in self.html).to(equal(True))

        with it("should put the class name in its own bold tag"):
            expect("<b>Catalog</b>" in self.html).to(equal(True))

        with it("should not put stereotypes inside the bold name"):
            expect("<b>Catalog &lt;&lt;Aggregate Root&gt;&gt;" in self.html).to(equal(False))
