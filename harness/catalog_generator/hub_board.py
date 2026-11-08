"""The catalog board: each practice's fidelities in the stage columns, the stage policies, and the actions and utilities
below them, as the hub and every detail page show it."""
from __future__ import annotations

import html

from harness.catalog_generator.approach_copy import StageCopy
from harness.catalog_generator.catalog_examples import StageExample
from harness.catalog_generator.stage_columns import STAGE_COLUMNS, BoardLabel, StageColumn

# The colour families the board cycles through for a stage's chips.
_CHIP_FAMILIES = ("sdd", "uxd", "arc")

_BOARD_SHELL = """
<div class="wrap">
<div class="foundry-kanban-shell" id="kanban-shell">
<section class="foundry-kanban-surface foundry-skills-expanded catalog-kanban-embed foundry-kanban-surface--cdd-always-expanded" id="catalog-kanban" aria-label="CDD catalog board"{attrs}>
  <div class="foundry-board-grid foundry-board-grid--cdd" id="board">
    {practice_col}
    {cols}
  </div>
  {stage_questions}
  <div class="foundry-skills-extra">
    <div class="foundry-skills-extra__inner">
      <div class="aad-delivery-crosscut-stack" data-id="crosscut">
        <section class="aad-delivery-crosscut-section aad-delivery-crosscut-section--supporting is-filter-visible">
          <h3 class="aad-delivery-crosscut-section-title">Actions</h3>
          <div class="aad-delivery-crosscut-section-body">
            <div class="aad-delivery-crosscut-row aad-crosscut-tier--practice is-filter-visible" data-crosscut-group="kanban" data-family="kanban">
              <span class="aad-delivery-crosscut-row-label aad-delivery-crosscut-row-label--spacer" aria-hidden="true"></span>
              <div class="aad-delivery-crosscut-skills is-skills-visible">{action_tickets}</div>
            </div>
          </div>
        </section>
        <section class="aad-delivery-crosscut-section aad-delivery-crosscut-section--foundational is-filter-visible">
          <h3 class="aad-delivery-crosscut-section-title">Utilities</h3>
          <div class="aad-delivery-crosscut-section-body">
            <div class="aad-delivery-crosscut-row aad-crosscut-tier--foundational is-filter-visible" data-crosscut-group="tools">
              <span class="aad-delivery-crosscut-row-label aad-delivery-crosscut-row-label--spacer" aria-hidden="true"></span>
              <div class="aad-delivery-crosscut-skills is-skills-visible">{utility_tickets}</div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</section>
</div>
</div>
"""

_POLICY_TOGGLE = (
    '<div class="kanban-stage-questions__spacer">'
    '<button type="button" class="policy-boxes-toggle" aria-expanded="false" '
    'aria-label="Show stage policies">'
    '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">'
    '<path d="M3 6l5 5 5-5" fill="none" stroke="currentColor" '
    'stroke-width="1.75" stroke-linecap="square" stroke-linejoin="miter"/>'
    "</svg></button></div>"
)


class HubBoard:
    """The board for one catalog: its practices in board order, its lifecycle actions and utilities (each with its
    ``name`` and page ``href``), and the approach's copy for each stage column. A practice page highlights its
    practice; a fidelity page highlights the fidelity too."""

    def __init__(self, practices: list, actions: list, utilities: list, stages: dict[str, StageCopy]) -> None:
        self.practices = practices
        self.actions = actions
        self.utilities = utilities
        self.stages = stages

    def html(self, *, path_prefix: str = "", practice=None, fidelity=None) -> str:
        """The board on a page ``path_prefix`` away from the hub, highlighting ``practice`` and its ``fidelity``."""
        return _BOARD_SHELL.format(
            attrs=self._highlight_attributes(practice, fidelity),
            practice_col=self._practice_rail(path_prefix),
            cols="".join(self._column(column, path_prefix, practice, fidelity) for column in STAGE_COLUMNS),
            stage_questions=self._stage_policies(path_prefix),
            action_tickets="".join(
                self._ticket(str(BoardLabel(action.name)), path_prefix + action.href, "aad-fam-supporting")
                for action in self.actions
            ),
            utility_tickets="".join(
                self._ticket(str(BoardLabel(utility.name)), path_prefix + utility.href, "aad-fam-foundational")
                for utility in self.utilities
            ),
        )

    def _stage(self, column: StageColumn) -> StageCopy:
        return self.stages.get(column.key) or StageCopy(id=column.stage.name)

    def _highlight_attributes(self, practice, fidelity) -> str:
        attributes = ' data-cdd-always-expanded="1" data-cdd-no-stage-filter="1"'
        if practice is None:
            return attributes
        attributes += f' data-initial-family="{html.escape(practice.key)}"'
        highlighted = self._highlighted_column(practice, fidelity)
        if highlighted is not None:
            attributes += f' data-initial-stage="{html.escape(highlighted.key)}"'
        return attributes

    def _highlighted_column(self, practice, fidelity) -> StageColumn | None:
        """The column holding ``fidelity`` in ``practice``'s place on the board; none when no fidelity is highlighted."""
        if practice is None or fidelity is None:
            return None
        return next((column for column in STAGE_COLUMNS if practice.fidelity_in(column) is fidelity), None)

    def _practice_rail(self, path_prefix: str) -> str:
        approach_head = (
            f'<a class="kb-ticket aad-skill aad-fam-delivery foundry-practice-col__card '
            f'foundry-practice-col__card--header foundry-practice-col__cdd-head '
            f'foundry-perspective-label foundry-perspective-label--cdd" '
            f'data-perspective="cdd" '
            f'href="{html.escape(path_prefix + "cdd-approach.html")}">{html.escape(str(BoardLabel("cdd")))}</a>'
        )
        practices = "".join(self._practice_card(practice, path_prefix + practice.href) for practice in self.practices)
        return f'<div class="foundry-practice-col" aria-label="Context tools">{approach_head}{practices}</div>'

    def _practice_card(self, practice, href: str) -> str:
        """A practice on the rail: it opens the practice page and does not filter the board."""
        perspective = practice.perspective
        return (
            f'<a class="kb-ticket aad-skill {practice.family} foundry-practice-col__card '
            f'foundry-perspective-label foundry-family-toggle foundry-perspective-label--{perspective}" '
            f'data-family="{html.escape(practice.key)}" data-perspective="{perspective}" '
            f'href="{html.escape(href)}" aria-pressed="false">{html.escape(practice.label)}</a>'
        )

    def _column(self, column: StageColumn, path_prefix: str, practice, fidelity) -> str:
        cells = "".join(self._cell(column, listed, path_prefix, fidelity) for listed in self.practices)
        active = " active" if self._highlighted_column(practice, fidelity) is column else ""
        example_href = StageExample(self._stage(column)).href(path_prefix)
        label = html.escape(column.label)
        title = (
            f'<a class="kb-col-head-title__link" href="{html.escape(example_href)}">{label}</a>'
            if example_href
            else f"<span>{label}</span>"
        )
        return (
            f'<div class="kb-col{active}" data-id="col-{column.key}" data-stage="{column.key}">'
            f'<div class="kb-col-head{" kb-col-head--current" if active else ""}">'
            f'<div class="kb-col-head-row">'
            f"{self._scope_shape(column)}"
            f'<span class="kb-col-head-title">{title}</span>'
            f"</div></div>"
            f"{self._stage_detail(column)}"
            f"{cells}"
            f"</div>"
        )

    def _cell(self, column: StageColumn, practice, path_prefix: str, highlighted_fidelity) -> str:
        fidelity = practice.fidelity_in(column)
        if fidelity is None:
            return f'<div class="aad-skill-row {practice.family} aad-skill-row--empty" data-family="{html.escape(practice.key)}"></div>'
        ticket = self._ticket(
            fidelity.label,
            path_prefix + practice.fidelity_href(fidelity.fidelity),
            practice.family,
            stage=column.key,
            perspective=practice.perspective,
            current=fidelity is highlighted_fidelity,
        )
        return f'<div class="aad-skill-row {practice.family}" data-family="{html.escape(practice.key)}">{ticket}</div>'

    def _ticket(
        self, label: str, href: str, family: str, *, stage: str = "", perspective: str = "", current: bool = False
    ) -> str:
        classes = f"kb-ticket aad-skill {family}" + (" kb-ticket--current" if current else "")
        data = (f' data-stage="{html.escape(stage)}"' if stage else "") + (
            f' data-perspective="{html.escape(perspective)}"' if perspective else ""
        )
        label = html.escape(label)
        return (
            f'<a class="{classes}"{data} href="{html.escape(href)}">'
            f'<span class="kb-skill-tooltip-wrap">{label}'
            f'<span class="kb-col-shape-tooltip kb-skill-tooltip" role="tooltip">'
            f'<span class="kb-col-shape-tooltip__name">{label}</span>'
            f"</span></span></a>"
        )

    def _scope_shape(self, column: StageColumn) -> str:
        scope = column.scope
        title = f"{scope.name} — {scope.reach} — {scope.covers}"
        aria = f"{scope.name}. {scope.reach}. {scope.covers.replace(' · ', ', ')}"
        return (
            f'<span class="kb-col-scope-shape-wrap">'
            f'<span class="kb-col-scope-shape kb-col-scope-shape--{html.escape(scope.shape)}" '
            f'title="{html.escape(title)}" aria-label="{html.escape(aria)}"></span>'
            f'<span class="kb-col-shape-tooltip" role="tooltip">'
            f'<span class="kb-col-shape-tooltip__name">{html.escape(scope.name)}</span>'
            f'<span class="kb-col-shape-tooltip__width">{html.escape(scope.reach)}</span>'
            f'<span class="kb-col-shape-tooltip__bullets">{html.escape(scope.covers)}</span>'
            f"</span></span>"
        )

    def _stage_detail(self, column: StageColumn) -> str:
        """The approach's chips and paragraphs for the stage, shown inside its column."""
        stage = self._stage(column)
        chips = "".join(
            f'<li class="tour-stage-detail__chip tour-stage-detail__chip--{_CHIP_FAMILIES[index % len(_CHIP_FAMILIES)]}">'
            f"{html.escape(item)}</li>"
            for index, item in enumerate(stage.items)
        )
        paragraphs = "".join(f'<p class="tour-stage-detail__desc">{html.escape(para)}</p>' for para in stage.paras)
        return (
            f'<div class="tour-stage-detail" data-stage-detail="{html.escape(column.key)}">'
            f'<ul class="tour-stage-detail__chips">{chips}</ul>'
            f"{paragraphs}"
            f"</div>"
        )

    def _stage_policies(self, path_prefix: str) -> str:
        cells = [_POLICY_TOGGLE]
        for column in STAGE_COLUMNS:
            stage = self._stage(column)
            items = "".join(f'<li class="kanban-stage-questions__item">{html.escape(item)}</li>' for item in stage.items)
            paragraphs = "".join(f'<p class="kanban-stage-questions__desc">{html.escape(para)}</p>' for para in stage.paras)
            href = f"{path_prefix}fidelities/cdd-{column.key}.html"
            cells.append(
                f'<a class="kanban-stage-questions__cell" data-stage="{html.escape(column.key)}" '
                f'href="{html.escape(href)}">'
                f'<ul class="kanban-stage-questions__list">{items}</ul>'
                f"{paragraphs}"
                f"</a>"
            )
        return (
            '<div class="kanban-stage-questions kanban-stage-questions--foundry '
            'kanban-stage-questions--cdd is-collapsed" data-id="stage-questions">'
            + "".join(cells)
            + "</div>"
        )
