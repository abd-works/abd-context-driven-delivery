"""Live check of class cards on a whiteboard: render read-only copies of pml-web's domain model (DDD) and object model
(Clean Engineering) to whiteboards in this folder, unpublished, and report, for each: classes the document has that no
card draws, cards with a rule under the name, the part split, folded classes spaced, and where invariants sit."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
COPIES = HERE / "pml-web-domain-model"

from harness.whiteboard.whiteboard import Whiteboard
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.whiteboard.whiteboard_bounded_context_map import WhiteboardBoundedContextMap
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model import WhiteboardCleanEngineeringModel


def judge(name: str, text: str, wanted: set) -> None:
    cards = [element.text for element in Whiteboard.from_text(text).elements if getattr(element, "role", "") in ("class", "imported")]
    drawn = {found for card in cards for found in re.findall(r"^\*\*([\w.]+)\*\*", card, re.M)}
    print(f"== {name}: {len(cards)} cards, {len(drawn)} classes drawn of {len(wanted)} the document has")
    print("   missing:", sorted(wanted - drawn) or "none")
    print("   rule under a name:", sum(1 for card in cards if re.search(r"^\*\*[\w.]+\*\*\n---$", card, re.M)))
    print("   cards with the – – – split:", sum(1 for card in cards if "– – –" in card))
    print("   folded classes not after a blank line:", sum(1 for card in cards for match in re.finditer(r"(?<!\n\n)(\*«[^\n]*»\*\n)?\*\*[\w.]+\*\*", card) if match.start() > 0 and card[:match.start()].strip() and not card[:match.start()].endswith("\n\n") and not card[:match.start()].rstrip().endswith("`") and not card[:match.start()].endswith("»*\n")))
    print("   cards with an invariant line:", sum(1 for card in cards if "\n  // " in card or "\n// " in card))
    print("   cards with an Invariants heading:", sum(1 for card in cards if "Invariants" in card))


domain = (COPIES / "domain-model.md").read_text(encoding="utf-8")
text = WhiteboardBoundedContextMap().render(MarkdownBoundedContextMap().parse(domain))
(HERE / "pml-web-domain-model.whiteboard").write_text(text, encoding="utf-8")
judge("pml-web domain model (DDD)", text, set(re.findall(r"^#### (\w+)", domain, re.M)) | set(re.findall(r"^\*\*(\w+)\*\* «Repository»", domain, re.M)))

objects = (COPIES / "src-model.md").read_text(encoding="utf-8")
text = WhiteboardCleanEngineeringModel().render(MarkdownCleanEngineeringModel().parse(objects))
(HERE / "pml-web-src-model.whiteboard").write_text(text, encoding="utf-8")
judge("pml-web object model (Clean Engineering)", text, set(re.findall(r"^#####\s+([\w.]+)", objects, re.M)))
