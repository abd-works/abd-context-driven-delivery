"""Mamba spec for the links of a diagram the draw.io viewer shows. Reported 2026-11-26: a story's link in the story map
showed "not found" at 127.0.0.1:8791/story_tests/..., since the browser read the link against the viewer. The viewer
now sends a link to a file through the Files server, and writes it back as it was when the diagram is saved."""

import html
import sys
import urllib.parse
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it

from tools.drawio_viewer.drawio_viewer import DiagramLinks

STORY_LINK = "../story_tests/register/register_story.test.md"
DIAGRAM = '<mxfile><UserObject label="Register" link="{story}" id="1"/><UserObject label="Map" link="story-map.md#e-register" id="2"/><UserObject label="Web" link="https://example.org/a?b=1&amp;c=2" id="3"/><UserObject label="Page" link="#data-page" id="4"/></mxfile>'.format(story=STORY_LINK)


def _link_of(xml: str, cell: str) -> str:
    """The link the cell with id cell carries in xml, as a browser reads it."""
    start = xml.index(f'id="{cell}"')
    attribute = xml.rindex('link="', 0, start) + len('link="')
    return html.unescape(xml[attribute:xml.index('"', attribute)])


with description("a diagram opened in the draw.io viewer") as self:
    with before.each:
        self.links = DiagramLinks("C:/dev/shop/.context/story-map.drawio", "http://127.0.0.1:8783", "C:/dev/shop", "chat-1", "ui-fixes")
        self.shown = self.links.sent_through_files(DIAGRAM)

    with context("with a link to a story file beside it"):
        with before.each:
            self.sent = urllib.parse.urlparse(_link_of(self.shown, "1"))

        with it("should send the link to the Files server's draw.io link route"):
            expect(f"{self.sent.scheme}://{self.sent.netloc}{self.sent.path}").to(equal("http://127.0.0.1:8783/api/drawio/link"))

        with it("should carry the link as the diagram holds it, with the diagram, project, chat and ticket"):
            query = {key: values[0] for key, values in urllib.parse.parse_qs(self.sent.query).items()}
            expect(query).to(equal({"diagram": "C:/dev/shop/.context/story-map.drawio", "project": "C:/dev/shop", "chat": "chat-1", "ticket": "ui-fixes", "link": STORY_LINK}))

    with context("with a link to a heading of a file beside it"):
        with it("should carry the heading's anchor in the link it sends"):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(_link_of(self.shown, "2")).query)
            expect(query["link"]).to(equal(["story-map.md#e-register"]))

    with context("with a link to a web page"):
        with it("should leave it as it is"):
            expect(_link_of(self.shown, "3")).to(equal("https://example.org/a?b=1&c=2"))

    with context("with a link to a page of the diagram itself"):
        with it("should leave it as it is"):
            expect(_link_of(self.shown, "4")).to(equal("#data-page"))

    with context("that is saved"):
        with it("should write every link back exactly as the diagram held it"):
            expect(self.links.written_back(self.shown)).to(equal(DIAGRAM))

    with context("opened by hand, with no chat or ticket named"):
        with it("should send the link without them"):
            shown = DiagramLinks("C:/dev/shop/.context/story-map.drawio", "http://127.0.0.1:8783", "C:/dev/shop").sent_through_files(DIAGRAM)
            expect(sorted(urllib.parse.parse_qs(urllib.parse.urlparse(_link_of(shown, "1")).query))).to(equal(["diagram", "link", "project"]))
