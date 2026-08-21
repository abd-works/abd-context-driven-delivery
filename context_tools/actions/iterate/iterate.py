# @toolset-manifest python -m tools manifest iterate.iterate:Iterator
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
# Do not author behavior from this Python source.
"""Iterate on formal generate output through a grill loop with validate + one fix pass.

Iterator is a standalone toolset. The complementary @iterate decorator (see
_decorator.py) marks an @action so framework composition prepends
iterate_session (which calls grill_with_context in-method).
"""
from __future__ import annotations

from grill_context.grill_context import GrillContext
from primitives.actions.action import action, agentic_toolset
from tools.tool import tool


@agentic_toolset
class Iterator:
    """Iterate formal generate output with scanners - tiny grilled slices only; never dump a whole artifact in one tick."""

    def _grill_context(self) -> GrillContext:
        """GrillContext toolset for in-method composition (not a tool)."""
        return GrillContext()

    @tool
    def mark_iterate_tick(self) -> str:
        """Record that an iterate show/validate/fix tick is due (no I/O).
        Call only after 2-3 grill answers that unlock ONE small slice - never as a prelude to dumping the whole artifact."""
        return "iterate-tick"

    @action
    def iterate(self, tools: list) -> str:
        """Iterate then generate - grill + formal generate/validate/one-fix ticks."""
        for host in self.context_tools(tools):
            host.open()
            host.decisions.record_decisions_session()
            self.iterate_session()
            host.generate()
        return "Iterate complete; generate instructions applied."

    @action
    def iterate_session(self, plan: str = "") -> str:
        """Iterate host generate output through an explicit grill_with_context call. Question shape (frame + options) comes from grill_with_context - do not restate bare options here. Each tick writes ONLY the slice unlocked by the last 2-3 answers, then validates and applies one fix pass. Filling the whole map/artifact from index, memory, or templates in one tick is a DEFECT - it defeats this tool."""
        """Step 0 - Grill the iterate plan (concept-grounded questions via grill_with_context). Ask ONE question at a time. Do not pre-author artifacts while grilling. grill_with_context prove-read applies every question: Read every relevant referenced context (segment, module-context, grill-answers, story-context, build-order, cited paths, ...) before options; index stubs are not inventory."""
        self._grill_context().grill_with_context(plan)
        """Step 1 - Resolve session roots the same way generate does (session.path for durable artifacts; session.folder for sprint process docs). If no sprint exists yet, confirm path, suggest a kebab slug, open, then continue."""
        """Step 2 - Hard gate before any generate: (a) the last 2-3 grill answers must name a concrete slice boundary (e.g. one epic, one activity, one increment, one module seam - not \"the whole product\"); (b) those answers must be grounded in a prove-read of the relevant referenced context files for that seam - not titles, memory, or an unread cited path. If the slice is still vague or referenced context was not prove-read, ask another grill question. Do NOT call mark_iterate_tick yet."""
        """Step 3 - After that gate passes, call mark_iterate_tick, then generate ONLY that unlocked slice via the host generate contract. Show the delta in chat. Unresolved branches stay explicit placeholders/TODOs or are simply omitted - never invent the rest of the tree \"to be helpful.\" Anti-patterns (DEFECT): writing a complete story-map/thin-slice/module set from an index in one tick; expanding every epic because scope was \"full handbook\"; treating generate's full template as permission to fill everything; proposing names from a skim of headings while leaving cited context unread."""
        self.mark_iterate_tick()
        """Step 4 - Run the host validate action (scanners) on the session-rooted artifacts just written. Show the validation report. Scope judgment to the tick's files when possible."""
        """Step 5 - Implement scanner fixes once via the host satisfy and/or repair path - still only within the unlocked slice. Do NOT re-scan or re-validate before the next grill question - one scan + one fix pass per tick. Remaining violations become grill fuel or the next iterate tick."""
        """Step 6 - STOP. Return to Step 0 and ask the next grill question. Do not chain ticks. Do not \"finish the rest\" in the same turn. Repeat grill -> tiny generate slice -> validate -> one fix until the user is satisfied or switches stage (sketch / plain generate)."""
        return "Iterate tick complete - one unlocked slice written, validated, and fixed once; resume grilling."
