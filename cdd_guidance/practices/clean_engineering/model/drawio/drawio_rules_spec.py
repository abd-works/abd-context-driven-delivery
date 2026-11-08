"""Draw.io graph rules — same XML fixtures as drawio scanner specs."""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import be_true, equal, expect
from mamba import before, context, description, it

from harness.graph.graph import Graph, Node, Source
from harness.guidance.guidance import PracticeGuidance
from harness.graph.rule_context import RuleCheckContext
from cdd_guidance.practices.clean_engineering.model.drawio.rules import BY_SLUG

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


def _drawio_node(practice: PracticeGuidance, root: Path, xml: str) -> Node:
    path = root / "model.drawio"
    path.write_text(xml, encoding="utf-8")
    node = Node(
        practice,
        "OoadClass",
        "clean_engineering:OoadClass:model.drawio:Prospect",
        "Prospect",
        Source("model.drawio", 1, 10),
    )
    practice.graph.open(root)
    practice.in_graph.hold(node)
    return node


with description("class-title-no-markdown-bold drawio graph rule"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.practice = Graph().practice("clean_engineering")
        self.rule = BY_SLUG["class-title-no-markdown-bold"]
        self.context = RuleCheckContext(self.practice, self.root)

    with context("a class title that still contains markdown bold markers"):
        with it("should report a violation on the diagram's class"):
            node = _drawio_node(self.practice, self.root, _FAULTY)
            hits = self.rule.check_practice(self.context)
            expect({node_id for node_id, _message in hits}).to(equal({node.node_id}))

    with context("a diagram the graph read two classes from"):
        with it("should scan the diagram once"):
            node = _drawio_node(self.practice, self.root, _FAULTY)
            self.practice.in_graph.hold(Node(self.practice, "OoadClass", "clean_engineering:OoadClass:model.drawio:Other", "Other", Source("model.drawio", 11, 20)))
            hits = self.rule.check_practice(self.context)
            expect(len(hits)).to(equal(len(self.rule.scanner.scan_file(self.root, self.root / "model.drawio"))))

    with context("a class title that is plain text inside the HTML bold tag"):
        with it("should produce no violations"):
            _drawio_node(self.practice, self.root, _CLEAN)
            expect(self.rule.check_practice(self.context)).to(equal([]))
