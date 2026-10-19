"""Draw.io graph rules — same XML fixtures as drawio scanner specs."""

import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from expects import be_true, equal, expect
from mamba import before, context, description, it

from graph import Node, PracticeGraph, Source
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


def _drawio_node(practice: PracticeGraph, root: Path, xml: str) -> Node:
    path = root / "model.drawio"
    path.write_text(xml, encoding="utf-8")
    node = Node(
        practice,
        "OoadClass",
        "clean_engineering:OoadClass:model.drawio:Prospect",
        "Prospect",
        Source("model.drawio", 1, 10),
    )
    practice.by_id[node.node_id] = node
    practice.nodes.setdefault("OoadClass", []).append(node)
    practice.source_root = str(root)
    return node


with description("class-title-no-markdown-bold drawio graph rule"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.practice = PracticeGraph("clean_engineering")
        self.rule = BY_SLUG["class-title-no-markdown-bold"]
        self.context = RuleCheckContext(self.practice, self.root)

    with context("a class title that still contains markdown bold markers"):
        with it("should report a violation"):
            node = _drawio_node(self.practice, self.root, _FAULTY)
            hits = self.rule.check(node, self.context)
            expect(len(hits) > 0).to(be_true)

    with context("a class title that is plain text inside the HTML bold tag"):
        with it("should produce no violations"):
            node = _drawio_node(self.practice, self.root, _CLEAN)
            expect(self.rule.check(node, self.context)).to(equal([]))
