"""Emit Stories-channel JS beside Python story-dict files (ensure-javascript helper)."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from practices.stories.model.javascript.spec_file import render_story_spec_file
from practices.stories.model.story_model import Example, StepType, Scenario, Step, Story


def load_story_dict(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'^("""[\s\S]*?"""\s*)+', "", text)
    tree = ast.parse(text)
    for node in tree.body:
        value = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Dict):
            value = node.value
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            value = node.value
        if value is not None:
            return ast.literal_eval(value)
    raise ValueError(f"no story dict in {path}")


def dict_to_story(data: dict) -> Story:
    story = Story(data["story"], 0)
    story.actors = [data["actor"]] if data.get("actor") else []
    story.domain_terms = list(data.get("domain_terms", ()))
    story.evidence = list(data.get("evidence", ()))
    flow = data.get("main_flow") or {}
    scenario = Scenario(flow.get("name", "main"), 0, story_name=story.name)
    order = 0
    for text in flow.get("given", ()):
        order += 1
        scenario.steps.append(Step(text, StepType.GIVEN, order))
    for block in flow.get("interactions", ()):
        for text in block.get("when", ()):
            order += 1
            scenario.steps.append(
                Step(text, StepType.WHEN, order, is_continuation=text.startswith(("And ", "But ")))
            )
        for text in block.get("then", ()):
            order += 1
            scenario.steps.append(
                Step(text, StepType.THEN, order, is_continuation=text.startswith(("And ", "But ")))
            )
    if flow.get("examples"):
        scenario.is_outline = True
        for index, row in enumerate(flow["examples"], start=1):
            label = str(row.get("example") or row.get("name") or f"example-{index}")
            scenario.examples.append(Example(label, index, dict(row)))
    story.scenarios.append(scenario)
    return story


def emit_story_javascript(
    path: Path,
    *,
    relative_types_path: str = "../../../../practices/stories/model/javascript/seeds/story-types",
) -> Path:
    """Write `<stem>.js` next to a Python story-dict file using the Stories JS renderer."""
    story = dict_to_story(load_story_dict(path))
    body = render_story_spec_file(story, relative_types_path=relative_types_path)
    body += f"\nexport const storyNames = ['{story.name}']\n"
    out = path.with_suffix(".js")
    out.write_text(body, encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    args = [Path(a) for a in (argv or sys.argv[1:])]
    if not args:
        print("usage: emit_story_javascript.py <story.py>...", file=sys.stderr)
        return 2
    for path in args:
        out = emit_story_javascript(path)
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
