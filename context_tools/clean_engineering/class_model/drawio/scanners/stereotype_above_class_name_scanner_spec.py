"""BDD: stereotype-above-class-name — <<Stereotype>> is above the name, not inside <b>."""
import sys
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import context, description, it

_HERE = Path(__file__).resolve().parent
_REPO = Path(__file__).resolve().parents[5]
for _p in (_REPO, _REPO / "primitives", _REPO / "utilities", _REPO / "context_tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
sys.path.insert(0, str(_HERE))

from stereotype_above_class_name_scanner import (  # noqa: E402
    StereotypeAboveClassNameScanner,
)
from _drawio_base import collect_drawio_files  # noqa: E402
from context_tools.clean_engineering.class_model.base_class_model import (  # noqa: E402
    OoadClass,
)
from context_tools.clean_engineering.class_model.drawio.drawio_class_model import (  # noqa: E402
    _build_class_html,
)

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


def _scan(xml: str):
    tmp = Path(tempfile.mkdtemp())
    path = tmp / "model.drawio"
    path.write_text(xml, encoding="utf-8")
    scanner = StereotypeAboveClassNameScanner("stereotype-above-class-name")
    files = collect_drawio_files(tmp)
    return scanner.scan(tmp, files)


with description("stereotype-above-class-name scanner"):
    with context("a class title that puts the stereotype inside the bold name"):
        with it("should report a violation"):
            violations = _scan(_FAULTY)
            expect(len(violations) > 0).to(equal(True))

    with context("a class title with the stereotype on its own italic line above the name"):
        with it("should produce no violations"):
            violations = _scan(_CLEAN)
            expect(violations).to(equal([]))

    with context("HTML emitted for a class whose name still carries tactical tags"):
        with it("should put stereotypes above the bold name"):
            html = _build_class_html(
                OoadClass("Catalog <<Aggregate Root>> <<Entity>>", sequential_order=1)
            )
            expect("&lt;&lt;Aggregate Root&gt;&gt;" in html).to(equal(True))
            expect("<b>Catalog</b>" in html).to(equal(True))
            expect("<b>Catalog &lt;&lt;Aggregate Root&gt;&gt;" in html).to(equal(False))
