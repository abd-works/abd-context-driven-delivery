"""BDD: class-title-no-markdown-bold — `**` must not appear in class titles."""
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.practices.clean_engineering.model.drawio.scanners.class_title_no_markdown_bold_scanner import (
    ClassTitleNoMarkdownBoldScanner,
)

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


class _ScannerExample(ClassTitleNoMarkdownBoldScanner):
    def scan_xml(self, xml: str):
        tmp = Path(tempfile.mkdtemp())
        path = tmp / "model.drawio"
        path.write_text(xml, encoding="utf-8")
        files = self.collect_drawio_files(tmp)
        return self.scan(tmp, files)


with description("class-title-no-markdown-bold scanner"):
    with context("a class title that still contains markdown bold markers"):
        with it("should report a violation"):
            violations = _ScannerExample("class-title-no-markdown-bold").scan_xml(_FAULTY)
            expect(len(violations) > 0).to(equal(True))

    with context("a class title that is plain text inside the HTML bold tag"):
        with it("should produce no violations"):
            violations = _ScannerExample("class-title-no-markdown-bold").scan_xml(_CLEAN)
            expect(violations).to(equal([]))
