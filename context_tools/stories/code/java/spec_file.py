"""Java spec-file renderer — emits one `<StoryPascalCase>Stories.java` per Story.

Shape produced (reference architecture, Java flavour):

    package <tests-root>.<epic-snake>.<sub-epic-snake>;

    import stories.StoryTypes.Story;
    import stories.StoryTypes.Scenario;
    import stories.StoryTypes.Interaction;
    import java.util.List;
    import java.util.Map;

    public final class <StoryPascalCase>Stories {
        public static final Story STORY = new Story() {
            @Override public String story()   { return "<Story Name>"; }
            @Override public String actor()   { return "<Actor>"; }
            @Override public List<String> domainTerms() { return List.of(...); }
            @Override public List<String> evidence()    { return List.of(...); }
            @Override public Map<String, Scenario> scenarios() {
                return Map.of(
                    "<scenarioKey>", new Scenario(
                        "<scenario name>",
                        List.of("given clause", ...),
                        List.of(new Interaction(List.of("when..."), List.of("then...")))
                    )
                );
            }
        };
    }

This file is FULLY regeneratable — it contains only data derived from the
canonical Scenario model. Tier files own hand-authored logic (write-once).
"""

from __future__ import annotations

import re
from typing import Iterable, List

from context_tools.stories.story_model.nodes import Story


def render_java_story_spec_file(
    story: Story,
    *,
    package_parts: List[str] | None = None,
) -> str:
    """Render one Story to a Java spec-file body.

    - `story` carries `name`, `users`, `domain_terms`, `evidence`, `scenarios`.
    - `package_parts` is the list of package segments (e.g.
      `["tests", "manage_customer_orders", "place_new_order"]`).
    """
    pkg = ".".join(package_parts) if package_parts else "stories"
    pascal = _pascal(story.name)
    actor = (story.users[0] if story.users else "").strip()
    scenarios = list(getattr(story, "scenarios", []) or [])

    lines: List[str] = []
    lines.append(f"package {pkg};")
    lines.append("")
    lines.append("import stories.StoryTypes.Story;")
    lines.append("import stories.StoryTypes.Scenario;")
    lines.append("import stories.StoryTypes.Interaction;")
    lines.append("import java.util.List;")
    lines.append("import java.util.Map;")
    lines.append("")
    lines.append(f"public final class {pascal}Stories {{")
    lines.append(f"    public static final Story STORY = new Story() {{")
    lines.append(f"        @Override public String story()  {{ return {_java_string(story.name)}; }}")
    lines.append(f"        @Override public String actor()  {{ return {_java_string(actor)}; }}")
    lines.append(f"        @Override public List<String> domainTerms() {{")
    lines.append(f"            return {_java_list(story.domain_terms)};")
    lines.append(f"        }}")
    lines.append(f"        @Override public List<String> evidence() {{")
    lines.append(f"            return {_java_list(story.evidence)};")
    lines.append(f"        }}")
    lines.append(f"        @Override public Map<String, Scenario> scenarios() {{")
    if scenarios:
        entries: List[str] = []
        for scenario in scenarios:
            key = _camel(scenario.name)
            entry = (
                f"                {_java_string(key)}, "
                f"{_render_scenario_expr(scenario)}"
            )
            entries.append(entry)
        # Map.of supports up to 10 entries; use Map.ofEntries for larger sets
        if len(entries) <= 10:
            lines.append("            return Map.of(")
            for i, entry in enumerate(entries):
                sep = "," if i < len(entries) - 1 else ""
                lines.append(f"{entry}{sep}")
            lines.append("            );")
        else:
            lines.append("            return Map.ofEntries(")
            for i, entry in enumerate(entries):
                sep = "," if i < len(entries) - 1 else ""
                lines.append(f"                Map.entry({entry.strip()}){sep}")
            lines.append("            );")
    else:
        lines.append("            return Map.of();")
    lines.append("        }")
    lines.append("    };")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _render_scenario_expr(scenario) -> str:
    given = _java_list([c.text for c in scenario.given])
    interaction_exprs = []
    for interaction in scenario.interactions:
        when_list = _java_list([c.text for c in interaction.when])
        then_list = _java_list([c.text for c in interaction.then])
        interaction_exprs.append(f"new Interaction({when_list}, {then_list})")
    interactions = f"List.of({', '.join(interaction_exprs)})" if interaction_exprs else "List.of()"
    return (
        f"new Scenario({_java_string(scenario.name)}, "
        f"{given}, {interactions})"
    )


_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_BACKTICK = re.compile(r"`([^`]+)`")


def _strip_md_emphasis(value: str) -> str:
    return _BACKTICK.sub(r"\1", _ITALIC.sub(r"\1", _BOLD.sub(r"\1", value)))


def _java_string(value: str) -> str:
    cleaned = _strip_md_emphasis(value)
    escaped = cleaned.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _java_list(values: Iterable[str]) -> str:
    items = list(values or [])
    if not items:
        return "List.of()"
    joined = ", ".join(_java_string(v) for v in items)
    return f"List.of({joined})"


def _pascal(name: str) -> str:
    parts = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    return "".join(w[:1].upper() + w[1:] for w in parts) or "Story"


def _camel(name: str) -> str:
    words = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    if not words:
        return "scenario"
    head = words[0][:1].lower() + words[0][1:]
    tail = "".join(w[:1].upper() + w[1:] for w in words[1:])
    return head + tail
