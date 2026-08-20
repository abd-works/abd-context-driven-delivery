"""BDD: class-title-no-markdown-bold — `**` must not appear in class titles."""
import sys
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

_HERE = Path(__file__).resolve().parent
_REPO = Path(__file__).resolve().parents[5]
for _p in (_REPO, _REPO / "primitives", _REPO / "utilities", _REPO / "context_tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
sys.path.insert(0, str(_HERE))

from class_title_no_markdown_bold_scanner import (  # noqa: E402
    ClassTitleNoMarkdownBoldScanner,
)
from _drawio_base import collect_drawio_files  # noqa: E402

_FAULTY = """\
<mxfile host="test">
  <diagram name="Page">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="2" vertex="1" parent="1" value="&lt;b&gt;**Prospect** &amp;lt;&amp;lt;Aggregate Root&amp;gt;&amp;gt;&lt;/b&gt;">
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
        <mxCell id="2" vertex="1" parent="1" value="&lt;b&gt;Prospect &amp;lt;&amp;lt;Aggregate Root&amp;gt;&amp;gt;&lt;/b&gt;">
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
    scanner = ClassTitleNoMarkdownBoldScanner("class-title-no-markdown-bold")
    files = collect_drawio_files(tmp)
    return scanner.scan(tmp, files)


with description("class-title-no-markdown-bold scanner"):
    with context("a class title that still contains markdown bold markers"):
        with it("should report a violation"):
            violations = _scan(_FAULTY)
            expect(len(violations) > 0).to(equal(True))

    with context("a class title that is plain text inside the HTML bold tag"):
        with it("should produce no violations"):
            violations = _scan(_CLEAN)
            expect(violations).to(equal([]))
