"""Render this repository's own models to whiteboard files in the session folder and judge the three arrow fixes."""
import re
import sys
import time
from pathlib import Path

ROOT = Path(r"C:\dev\abd-cdd-ui-fixes-as-i-use-it")
sys.path.insert(0, str(ROOT))
OUT = ROOT / ".sessions" / "ui-fixes-as-i-use-it" / "live-check"
OUT.mkdir(parents=True, exist_ok=True)

from harness.whiteboard.whiteboard import Arrow, Section, Shape, Whiteboard
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.whiteboard.whiteboard_bounded_context_map import WhiteboardBoundedContextMap
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model import WhiteboardCleanEngineeringModel

spec = ROOT / "cdd_guidance/practices/clean_engineering/model/whiteboard/whiteboard_class_model_spec.py"
source = spec.read_text(encoding="utf-8")
source = re.sub(r"\nwith description\(.*?(?=\n(?:def |class )|\Z)", "\n", source, flags=re.S)
helpers = {}
exec(source, helpers)
drawn_route, runs_through = helpers["drawn_route"], helpers["runs_through"]


def judge(name, text):
    board = Whiteboard.from_text(text)
    shapes = {element.id: element.box for element in board.elements if isinstance(element, Shape)}
    names = {element.id: (element.text.split("**")[1] if "**" in element.text else element.id) for element in board.elements if isinstance(element, Shape)}
    pages = [element for element in board.elements if isinstance(element, Section) and element.role == "page"]
    arrows = [element for element in board.elements if isinstance(element, Arrow) and element.from_id in shapes and element.to_id in shapes]
    pairs = {}
    for arrow in arrows:
        pairs.setdefault(frozenset((arrow.from_id, arrow.to_id)), []).append(arrow.role)
    beside = [sorted(names[i] for i in pair) for pair, roles in pairs.items() if "dependency" in roles and len(roles) > 1]
    print(f"== {name}: {len(arrows)} arrows, {len(pages)} pages")
    print("  1. dependency beside a solid relationship:", beside or "none")
    straight = [(names[a.from_id], names[a.to_id]) for a in arrows if not a.bends and a.from_side == "bottom" and a.to_side == "top"]
    stacked_down = [(names[a.from_id], names[a.to_id], a.bends) for a in arrows if a.bends and a.from_side == "bottom" and a.to_side == "top"]
    print("  2. straight down arrows:", len(straight), "| bent down arrows:", len(stacked_down))
    legs = {}
    for arrow in arrows:
        if arrow.bends and len(arrow.bends) == 2 and arrow.bends[0] == "v":
            start, end = shapes[arrow.from_id], shapes[arrow.to_id]
            height = start.y + start.h / 2 + arrow.bends[1]
            low, high = sorted((start.center[0], end.center[0]))
            legs.setdefault((arrow.from_id, arrow.from_side), []).append((height, low, high, names[arrow.to_id]))
    overlaps = [(names[key[0]], first[3], second[3]) for key, found in legs.items() for index, first in enumerate(found) for second in found[index + 1:]
                if first[0] == second[0] and min(first[2], second[2]) > max(first[1], second[1])]
    print("  2. level legs from one card side drawn over each other:", overlaps or "none")
    across = [arrow for arrow in arrows if "across" in arrow.id]
    through = []
    for arrow in across:
        route = drawn_route(arrow, shapes[arrow.from_id], shapes[arrow.to_id])
        own = [page for page in pages if page.box.overlaps(shapes[arrow.from_id]) or page.box.overlaps(shapes[arrow.to_id])]
        through += [(names[arrow.from_id], names[arrow.to_id], page.text) for page in pages if page not in own and runs_through(route, page.box)]
    print(f"  3. cross-page arrows: {len(across)}, of which with sides: {sum(1 for a in across if a.from_side)}; passing through a page they do not join: {through or 'none'}")
    return board


for title, path, reader, writer in [
    ("domain model (test-area/pml-web copy in this repo)", ROOT / "test-area/pml-web/src/.context/domain-model.md", MarkdownBoundedContextMap, WhiteboardBoundedContextMap),
    ("space class model", ROOT / "space/.context/space-model.md", MarkdownCleanEngineeringModel, WhiteboardCleanEngineeringModel),
]:
    began = time.time()
    text = writer().render(reader().parse(path.read_text(encoding="utf-8")))
    took = time.time() - began
    out = OUT / (path.stem + ".whiteboard")
    out.write_text(text, encoding="utf-8")
    print(f"rendered {path.name} in {took:.1f} s -> {out}")
    judge(title, text)
