"""The two formats a front-end view is written in, TypeScript and JavaScript: each reads a view from its text and
writes a view as its own language."""

from __future__ import annotations

from harness.guidance.practice_formats import FormatAdapter, Reshaped, Written

from cdd_guidance.practices.ux.model.view.front_end_view import FrontEndView
from cdd_guidance.practices.ux.model.view.reshaped_view import ReshapedView


class ViewFormat(FormatAdapter):
    """What both formats of a front-end view do the same way: write a rendered view onto a view file already there."""

    def reshape(self, rendered: str, existing: str) -> Reshaped:
        """existing, the file's text now, in the shape rendered has, losing no line of it: a component both hold keeps
        its body, a prop, hook or handler only rendered holds arrives empty, and one only existing holds stays, under
        a line that says it is no longer in the model."""
        return ReshapedView(self.parse(rendered), self.parse(existing)).reshaped()


class TypeScriptView(ViewFormat):
    """The ``typescript`` format of a front-end view: it reads a view written with types, and writes a view as
    TypeScript, which for a view read from JavaScript is that JavaScript as it is."""

    def parse(self, text: str, file: str = "") -> FrontEndView:
        return FrontEndView(text or "", typed=True)

    def render(self, view: FrontEndView, written: Written = Written()) -> str:
        return view.text


class JavaScriptView(ViewFormat):
    """The ``javascript`` format of a front-end view: it reads a view written without types, and writes a view as
    JavaScript, its type annotations dropped."""

    def parse(self, text: str, file: str = "") -> FrontEndView:
        return FrontEndView(text or "", typed=False)

    def render(self, view: FrontEndView, written: Written = Written()) -> str:
        return view.without_types

