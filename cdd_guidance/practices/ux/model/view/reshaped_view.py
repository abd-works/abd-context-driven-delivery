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

from harness.guidance.practice_formats import KeptMark, Reshaped

from cdd_guidance.practices.ux.model.view.front_end_view import Component, ComponentMember, Edit, FrontEndView

_PRIVATE_MARK = "_"


class ReshapedView:
    """One rendered view written onto the view a file already holds, losing nothing: the edits that add what only the
    render holds and mark what only the file holds, and the members each of those is."""

    def __init__(self, rendered: FrontEndView, existing: FrontEndView) -> None:
        self._rendered = rendered
        self._existing = existing
        self._edits: list[Edit] = []
        self._new_components: list[str] = []
        self._kept: list[str] = []
        self._added: list[str] = []

    def reshaped(self) -> Reshaped:
        """The file's text in the rendered shape, with the members kept though the model lacks them and those added."""
        held = {component.name: component for component in self._existing.components}
        for shape in self._rendered.components:
            if shape.name in held:
                self._reshape(held[shape.name], shape)
            else:
                self._added.append(shape.name)
                self._new_components.append(shape.text)
        text = self._existing.edited(self._edits)
        for component in self._new_components:
            text = f"{text}\n{component}" if text.endswith("\n") or not text else f"{text}\n\n{component}"
        return Reshaped(text, self._kept, self._added)

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
        self._kept.append(f"{held.name}.{member.name}")
        if not held.marked(member):
            marking = f"{KeptMark.WORDS}: {held.name}.{member.name}. Move its body into the member that replaced it, then delete it."
            self._edits.append(Edit(member.lead, member.lead, f"{held.indent_of(member.start)}// ---- {marking} ----\n"))

    def _add(self, held: Component, member: ComponentMember) -> None:
        """Name member as added, and write it into the component: a hook after its hooks, a handler, empty, before
        what it returns."""
        self._added.append(f"{held.name}.{member.name}")
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
            self._kept.append(f"{held.name}.{prop}")
            named = f"{held.name}.{prop}"
            if not any(KeptMark.marks(line) and named in line for line in held.marks.splitlines()):
                marking = f"{KeptMark.WORDS}: {named}, a prop. Take it out of the component's props once nothing reads it."
                self._edits.append(Edit(held.start, held.start, f"{held.indent_of(held.start)}// ---- {marking} ----\n"))
        gained = [prop for prop in shape.props if prop not in held.props]
        self._added.extend(f"{held.name}.{prop}" for prop in gained)
        if gained:
            self._take_props(held, gained)

    def _take_props(self, held: Component, gained: list[str]) -> None:
        """Write gained among the props held takes apart: each on a line of its own where the props are listed one to
        a line, else at the end of their line, with the opening line as it was kept above as a comment."""
        text = self._existing.text
        opening, closing = held.props_braces
        if "\n" in text[opening:closing]:
            last = len(text[:closing].rstrip())
            item_indent = held.indent_below(opening)
            comma = "" if text[last - 1] == "," else ","
            self._edits.append(Edit(last, last, comma + "".join(f"\n{item_indent}{prop}," for prop in gained)))
            return
        inner = text[opening + 1:closing]
        taken = f"{inner.rstrip()}, {', '.join(gained)}{inner[len(inner.rstrip()):]}"
        self._edits.append(Edit(held.start, held.start, f"{held.indent_of(held.start)}// {held.opening_line.strip()}\n"))
        self._edits.append(Edit(opening + 1, closing, taken))
