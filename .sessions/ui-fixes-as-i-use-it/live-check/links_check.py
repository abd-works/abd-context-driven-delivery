"""Live check of the diagram links: render this repository's story map and one class model to draw.io and to a
whiteboard into the session folder, unpublished, and confirm every link names a file that is there.

Each render is handed the folder of its source as the folder it is written in, as the render action does, so the links
are made from there; the files are then saved in the session folder."""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent

from harness.guidance.practice_formats import Written
from harness.whiteboard.whiteboard import Whiteboard
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryMap
from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryMap
from cdd_guidance.practices.stories.model.whiteboard.nodes import WhiteboardStoryMap
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model import WhiteboardCleanEngineeringModel
from harness.markdown.markdown import MarkdownText, heading_anchor

_WEB = re.compile(r"\]\((https://github\.com/[^/]+/[^/]+/blob/[^/]+/([^)#]+)(#[^)]*)?)\)")


def resolves(path: Path, anchor: str) -> bool:
    """Whether path is there and, for a markdown heading anchor, a heading of it has that anchor."""
    if not path.is_file():
        return False
    if not anchor or anchor.startswith("L") or path.suffix != ".md":
        return True
    return any(heading_anchor(words) == anchor or re.fullmatch(rf"{re.escape(heading_anchor(words))}-\d+", anchor) for *_rest, words in MarkdownText(path.read_text(encoding="utf-8")).headings())


def judge_drawio(name: str, text: str, folder: Path) -> None:
    links = [holder.get("link", "") for holder in ET.fromstring(text).iter("UserObject") if holder.get("link")]
    broken = [link for link in links if not resolves(folder / link.partition("#")[0], link.partition("#")[2])]
    kinds = {}
    for link in links:
        kinds[Path(link.partition("#")[0]).name.split("_story")[0] and Path(link.partition("#")[0]).suffix + (" story file" if "_story." in link else "")] = 0
    print(f"{name}: {len(links)} links, broken: {broken or 'none'}")
    print("   e.g.", links[:3], "| to story files:", sum(1 for link in links if "_story." in link))


def judge_board(name: str, text: str) -> None:
    found = [(match.group(2), (match.group(3) or "#")[1:]) for element in Whiteboard.from_text(text).elements for match in _WEB.finditer(getattr(element, "text", "") or "")]
    broken = [path for path, anchor in found if not resolves(ROOT / path, anchor)]
    print(f"{name}: {len(found)} links, broken: {broken or 'none'}")
    print("   e.g.", found[:3])


story_folder = ROOT / ".context"
story_map = MarkdownStoryMap().parse((story_folder / "story-map.md").read_text(encoding="utf-8"))
drawio = DrawIOStoryMap().render(story_map, Written(folder=story_folder))
(OUT / "story-map.drawio").write_text(drawio, encoding="utf-8")
judge_drawio("story map, draw.io", drawio, story_folder)
board = WhiteboardStoryMap().render(story_map, Written(folder=story_folder))
(OUT / "story-map.whiteboard").write_text(board, encoding="utf-8")
judge_board("story map, whiteboard", board)

model_file = ROOT / "cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md"
model = MarkdownCleanEngineeringModel().parse(model_file.read_text(encoding="utf-8"))
classes = sum(len(module.classes) for module in model.modules)
drawio = DrawIOCleanEngineeringModel().render(model, Written(folder=model_file.parent))
(OUT / "ooad-model.drawio").write_text(drawio, encoding="utf-8")
print(f"ooad model: {classes} classes")
judge_drawio("ooad class model, draw.io", drawio, model_file.parent)
model = MarkdownCleanEngineeringModel().parse(model_file.read_text(encoding="utf-8"))
board = WhiteboardCleanEngineeringModel().render(model, Written(folder=model_file.parent))
(OUT / "ooad-model.whiteboard").write_text(board, encoding="utf-8")
judge_board("ooad class model, whiteboard", board)
