"""Canonical BDD describe tree — parse a sketch, render python or typescript."""

from __future__ import annotations

from practices.bdd.model.nodes import Context, Description, Observation


class BddModel:
    def __init__(self) -> None:
        self.descriptions: list[Description] = []

    def parse(self, text: str) -> "BddModel":
        self.descriptions = _parse_sketch(text)
        return self

    def render(self, canonical: "BddModel", previous: str | None = None) -> str:
        return "\n\n".join(_render_python(item) for item in canonical.descriptions)


class PythonBddModel(BddModel):
    def render(self, canonical: BddModel, previous: str | None = None) -> str:
        return "\n\n".join(_render_python(item) for item in canonical.descriptions)


class TypeScriptBddModel(BddModel):
    def render(self, canonical: BddModel, previous: str | None = None) -> str:
        return "\n\n".join(_render_typescript(item) for item in canonical.descriptions)


class MarkdownBddModel(BddModel):
    def render(self, canonical: BddModel, previous: str | None = None) -> str:
        return "\n\n".join(_render_sketch(item) for item in canonical.descriptions)


def _parse_sketch(text: str) -> list[Description]:
    descriptions: list[Description] = []
    description: Description | None = None
    stack: list[tuple[int, Context]] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith(("//", "#", "->", "Fidelity:", "```")):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        level = indent // 2
        if stripped.startswith("it "):
            if not stack:
                continue
            stack[-1][1].observations.append(
                Observation(stripped[3:].strip(), len(stack[-1][1].observations) + 1)
            )
            continue
        if level == 0:
            description = Description(stripped, len(descriptions) + 1)
            descriptions.append(description)
            stack = []
            continue
        if description is None:
            continue
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1].contexts if stack else description.contexts
        context = Context(stripped, len(parent) + 1)
        parent.append(context)
        stack.append((level, context))
    return descriptions


def _render_python(description: Description) -> str:
    lines = [
        "from mamba import description, context, it",
        "from expects import expect",
        "",
        f'with description("{_escape(description.name)}"):',
    ]
    if not description.contexts:
        lines.append("    pass")
    for child in description.contexts:
        lines.extend(_python_context(child, 1))
    return "\n".join(lines) + "\n"


def _python_context(node: Context, depth: int) -> list[str]:
    pad = "    " * depth
    lines = [f'{pad}with context("{_escape(node.name)}"):']
    body = False
    for observation in node.observations:
        body = True
        lines.append(f'{pad}    with it("{_escape(observation.name)}"):')
        lines.append(f"{pad}        # BDD: SIGNATURE")
    for child in node.contexts:
        body = True
        lines.extend(_python_context(child, depth + 1))
    if not body:
        lines.append(f"{pad}    pass")
    return lines


def _render_typescript(description: Description) -> str:
    lines = [
        'import { describe, it } from "vitest";',
        "",
        f'describe("{_escape(description.name)}", () => {{',
    ]
    if not description.contexts:
        lines.append("  // BDD: SIGNATURE")
    for child in description.contexts:
        lines.extend(_typescript_context(child, 1))
    lines.append("});")
    return "\n".join(lines) + "\n"


def _typescript_context(node: Context, depth: int) -> list[str]:
    pad = "  " * depth
    lines = [f'{pad}describe("{_escape(node.name)}", () => {{']
    for observation in node.observations:
        lines.append(f'{pad}  it("{_escape(observation.name)}", () => {{')
        lines.append(f"{pad}    // BDD: SIGNATURE")
        lines.append(f"{pad}  }});")
    for child in node.contexts:
        lines.extend(_typescript_context(child, depth + 1))
    if not node.observations and not node.contexts:
        lines.append(f"{pad}  // BDD: SIGNATURE")
    lines.append(f"{pad}}});")
    return lines


def _render_sketch(description: Description) -> str:
    lines = [description.name]
    for child in description.contexts:
        lines.extend(_sketch_context(child, 1))
    return "\n".join(lines) + "\n"


def _sketch_context(node: Context, depth: int) -> list[str]:
    pad = "  " * depth
    lines = [f"{pad}{node.name}"]
    for observation in node.observations:
        lines.append(f"{pad}  it {observation.name}")
    for child in node.contexts:
        lines.extend(_sketch_context(child, depth + 1))
    return lines


def _escape(name: str) -> str:
    return name.replace("\\", "\\\\").replace('"', '\\"')
