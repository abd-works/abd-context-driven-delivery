"""A front-end view written onto a view file that is already there: the file takes the new shape and loses nothing.

A view file holds what its model does not: the bodies of its handlers, comments, imports, helpers, the types a person
wrote. So a render onto a view file edits the file instead of replacing it:

- A component both hold keeps its body as the file has it.
- A prop, a hook, or a handler only the render holds is **added**: a prop beside the props the component takes, a hook
  after its hooks as the render declares it, a handler before what the component returns, with an empty body. A
  component only the render holds is written after the file's own, as the render wrote it.
- A prop, a hook, or a handler only the file holds is **kept** where it is, under a line that says it is no longer in
  the model, so the view still runs; a person or an agent moves its body into the member that replaced it and then
  deletes it. A name that starts with an underscore is the file's own helper and is left alone, as is a component only
  the file holds, an import, and everything outside a component.

A line of the file is never dropped: where a component's opening line changes, to take a prop, the line as it was stays
above it as a comment. Rendering the same view onto the text this made changes nothing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from harness.guidance.practice_formats import Reshaped

from cdd_guidance.practices.ux.model.view.front_end_view import Edit, FrontEndView, TypeAnnotations

# What marks a member kept in a file though its model no longer holds it; a later render reads it to leave the member be.
NO_LONGER_IN_MODEL = "no longer in the model"
_COMMENT_STARTS = ("//", "/*", "*")
_FUNCTION = re.compile(r"[ \t]*(?:async[ \t]+)?function[ \t]+(?P<name>[\w$]+)[^(\n]*\(")
_DECLARED = re.compile(r"[ \t]*(?:const|let)[ \t]+(?P<pattern>[\w$]+|\[[^\]\n]*\]|\{[^}\n]*\})")
_ASSIGNED = re.compile(r"=(?![>=])")
_HOOK = re.compile(r"\s*use[A-Z][\w$]*\b")
_FUNCTION_VALUE = re.compile(r"\s*(?:async\s+)?function\b[^(\n]*\(")
_ARROW_PARAMETERS = re.compile(r"\s*(?:async\s*)?\(")
_ARROW_OF_ONE = re.compile(r"\s*(?:async\s+)?[\w$]+\s*=>")
_RETURN = re.compile(r"[ \t]*return\b")
_FIRST_NAME = re.compile(r"[\w$]+")
_PRIVATE_MARK = "_"


@dataclass(frozen=True)
class ComponentMember:
    """A hook or a handler a component declares: its name, the place the comments above it start, the places its own
    lines start and end, and how a render writes it into a file that lacks it (a handler empty, a hook as declared)."""

    name: str
    lead: int
    start: int
    end: int
    is_hook: bool
    written_new: str


class Component:
    """One component of a view, read from its text: its props, the hooks and handlers its body declares, and the places
    a render writes into."""

    def __init__(self, view: FrontEndView, name: str, opening: int) -> None:
        self._view = view
        self._text = view.scanned
        self._annotations = TypeAnnotations(view.scanned)
        self.name = name
        self.opening = opening
        self.start = self._text.line_start(opening)
        self.lead = self._lead_of(self.start)
        self.props = view.taken_apart(opening)
        self._body = self._annotations.body_after(self._text.closing(opening))
        self.members = self._members() if self._body >= 0 else []

    @property
    def end(self) -> int:
        """The place after the component's last line: after its body, or after the statement of one with no body in
        braces."""
        if self._body >= 0:
            return self._text.line_end(self._text.closing(self._body))
        return self._statement_end(self._text.closing(self.opening))

    @property
    def text(self) -> str:
        """The component as it is written, with the comments above it."""
        return self._text.text[self.lead:self.end]

    @property
    def marks(self) -> str:
        """The comments written above the component, where a line says which of its props are no longer in the model."""
        return self._text.text[self.lead:self.start]

    @property
    def opening_line(self) -> str:
        return self._text.text[self.start:self._text.line_end(self.start)].rstrip("\n")

    @property
    def props_braces(self) -> tuple[int, int]:
        """The places of the braces the component takes its props apart in."""
        inner = self._text.past_space(self.opening + 1)
        return inner, self._text.closing(inner)

    @property
    def new_handlers_at(self) -> int:
        """Where a handler the render adds is written: before what the component returns, with the comments above
        that; before the brace that closes its body when it returns nothing there."""
        returned = next((start for start in self._own_line_starts() if _RETURN.match(self._text.code, start)), -1)
        return self._lead_of(returned) if returned >= 0 else self._text.line_start(self._text.closing(self._body))

    @property
    def new_hooks_at(self) -> int:
        """Where a hook the render adds is written: after the last hook the component declares, else where its body
        starts."""
        hooks = [member.end for member in self.members if member.is_hook]
        return max(hooks) if hooks else self._text.line_end(self._body)

    def marked(self, member: ComponentMember) -> bool:
        """Whether an earlier render set the member apart: its marking line is among the comments above it."""
        return NO_LONGER_IN_MODEL in self._text.text[member.lead:member.start]

    def indent_of(self, position: int) -> str:
        line = self._text.text[self._text.line_start(position):]
        return line[:len(line) - len(line.lstrip(" \t"))]

    def _lead_of(self, start: int) -> int:
        """The place the comment lines written directly above the line at start begin; start when none are."""
        text, lead = self._text.text, start
        while lead > 0:
            above = self._text.line_start(lead - 1)
            if not text[above:lead].strip().startswith(_COMMENT_STARTS):
                break
            lead = above
        return lead

    def _own_line_starts(self) -> list[int]:
        """The start of each line of the body that is the component's own, outside the brackets of any member."""
        code, starts, depth = self._text.code, [], 0
        for position in range(self._body + 1, self._text.closing(self._body)):
            character = code[position]
            depth += (character in "([{") - (character in ")]}")
            if character == "\n" and depth == 0:
                starts.append(position + 1)
        return starts

    def _members(self) -> list[ComponentMember]:
        found = (self._function_at(start) or self._declared_at(start) for start in self._own_line_starts())
        return [member for member in found if member is not None]

    def _function_at(self, start: int) -> ComponentMember | None:
        """The handler declared with `function` on the line at start; none when the line declares none."""
        declared = _FUNCTION.match(self._text.code, start)
        body = self._annotations.body_after(self._text.closing(declared.end() - 1)) if declared is not None else -1
        if body < 0:
            return None
        end = self._text.line_end(self._text.closing(body))
        return ComponentMember(declared.group("name"), self._lead_of(start), start, end, False, f"{self._text.text[start:body]}{{}}")

    def _declared_at(self, start: int) -> ComponentMember | None:
        """The hook or the handler a `const` on the line at start declares; none for a plain value."""
        code = self._text.code
        declared = _DECLARED.match(code, start)
        assigned = _ASSIGNED.search(code, declared.end(), self._text.line_end(start)) if declared is not None else None
        if assigned is None:
            return None
        name = _FIRST_NAME.search(declared.group("pattern")).group()
        end = self._statement_end(assigned.end())
        if _HOOK.match(code, assigned.end()):
            return ComponentMember(name, self._lead_of(start), start, end, True, self._text.text[start:end].rstrip("\n"))
        empty = self._empty_function_from(assigned.end())
        return ComponentMember(name, self._lead_of(start), start, end, False, f"{self._text.text[start:empty]} {{}};") if empty >= 0 else None

    def _empty_function_from(self, assigned_at: int) -> int:
        """Where the function assigned at assigned_at stops being its heading and starts being its body: after its
        `=>`, or before the brace of one written with `function`; -1 when what is assigned there is no function."""
        code = self._text.code
        of_one = _ARROW_OF_ONE.match(code, assigned_at)
        if of_one is not None:
            return of_one.end()
        parameters = _ARROW_PARAMETERS.match(code, assigned_at) or _FUNCTION_VALUE.match(code, assigned_at)
        if parameters is None:
            return -1
        closing = self._text.closing(parameters.end() - 1)
        arrow = self._annotations.arrow_after(closing)
        if arrow >= 0:
            return arrow
        body = self._annotations.body_after(closing)
        return len(self._text.text[:body].rstrip()) if body >= 0 else -1

    def _statement_end(self, position: int) -> int:
        """The place after the line the statement that holds position ends on: its semicolon, or its line's end,
        outside any bracket it opens."""
        code, depth = self._text.code, 0
        while position < len(code):
            character = code[position]
            if depth <= 0 and character in ";\n":
                break
            depth += (character in "([{") - (character in ")]}")
            position += 1
        return self._text.line_end(min(position, len(code) - 1)) if code else 0


class ReshapedView:
    """One rendered view written onto the view a file already holds, losing nothing: the edits that add what only the
    render holds and mark what only the file holds, and the members each of those is."""

    def __init__(self, rendered: FrontEndView, existing: FrontEndView) -> None:
        self._rendered = rendered
        self._existing = existing
        self._edits: list[Edit] = []
        self._new_components: list[str] = []
        self.kept: list[str] = []
        self.added: list[str] = []

    def reshaped(self) -> Reshaped:
        """The file's text in the rendered shape, with the members kept though the model lacks them and those added."""
        held = {name: Component(self._existing, name, opening) for name, opening in self._existing.declared_components()}
        for name, opening in self._rendered.declared_components():
            shape = Component(self._rendered, name, opening)
            if name in held:
                self._reshape(held[name], shape)
            else:
                self.added.append(name)
                self._new_components.append(shape.text)
        text = self._existing.scanned.edited(self._edits)
        for component in self._new_components:
            text = f"{text}\n{component}" if text.endswith("\n") or not text else f"{text}\n\n{component}"
        return Reshaped(text, self.kept, self.added)

    def _reshape(self, held: Component, shape: Component) -> None:
        self._reshape_props(held, shape)
        in_file = {member.name for member in held.members}
        in_shape = {member.name for member in shape.members}
        for member in held.members:
            if member.name not in in_shape and not member.name.startswith(_PRIVATE_MARK):
                self._keep(held, member)
        for member in shape.members:
            if member.name not in in_file:
                self._add(held, member)

    def _keep(self, held: Component, member: ComponentMember) -> None:
        """Name member as kept, and mark it where it is unless an earlier render marked it."""
        self.kept.append(f"{held.name}.{member.name}")
        if not held.marked(member):
            marking = f"{NO_LONGER_IN_MODEL}: {held.name}.{member.name}. Move its body into the member that replaced it, then delete it."
            self._edits.append(Edit(member.lead, member.lead, f"{held.indent_of(member.start)}// ---- {marking} ----\n"))

    def _add(self, held: Component, member: ComponentMember) -> None:
        """Name member as added, and write it into the component: a hook after its hooks, a handler, empty, before
        what it returns."""
        self.added.append(f"{held.name}.{member.name}")
        if member.is_hook:
            self._edits.append(Edit(held.new_hooks_at, held.new_hooks_at, f"{member.written_new}\n"))
        else:
            self._edits.append(Edit(held.new_handlers_at, held.new_handlers_at, f"{member.written_new}\n\n"))

    def _reshape_props(self, held: Component, shape: Component) -> None:
        """Mark each prop only the file's component takes, and have it take each prop only the render's takes. A
        component that takes its props whole, in the file or in the render, is left as it is."""
        if not held.props or not shape.props:
            return
        for prop in (prop for prop in held.props if prop not in shape.props):
            self.kept.append(f"{held.name}.{prop}")
            named = f"{held.name}.{prop}"
            if not any(NO_LONGER_IN_MODEL in line and named in line for line in held.marks.splitlines()):
                marking = f"{NO_LONGER_IN_MODEL}: {named}, a prop. Take it out of the component's props once nothing reads it."
                self._edits.append(Edit(held.start, held.start, f"{held.indent_of(held.start)}// ---- {marking} ----\n"))
        gained = [prop for prop in shape.props if prop not in held.props]
        self.added.extend(f"{held.name}.{prop}" for prop in gained)
        if gained:
            self._take_props(held, gained)

    def _take_props(self, held: Component, gained: list[str]) -> None:
        """Write gained among the props held takes apart: each on a line of its own where the props are listed one to
        a line, else at the end of their line, with the opening line as it was kept above as a comment."""
        text = self._existing.scanned.text
        opening, closing = held.props_braces
        if "\n" in text[opening:closing]:
            last = len(text[:closing].rstrip())
            item_indent = held.indent_of(self._existing.scanned.line_end(opening))
            comma = "" if text[last - 1] == "," else ","
            self._edits.append(Edit(last, last, comma + "".join(f"\n{item_indent}{prop}," for prop in gained)))
            return
        inner = text[opening + 1:closing]
        taken = f"{inner.rstrip()}, {', '.join(gained)}{inner[len(inner.rstrip()):]}"
        self._edits.append(Edit(held.start, held.start, f"{held.indent_of(held.start)}// {held.opening_line.strip()}\n"))
        self._edits.append(Edit(opening + 1, closing, taken))
