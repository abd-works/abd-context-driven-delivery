"""scenarios-shape - validates the fundamental Gherkin skeleton."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


class ScenariosShapeScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_scenarios():
            yield self.violation(
                "No scenarios found",
                location="scenarios/",
                severity="error",
            )
            return

        for scenario in workspace.scenarios:
            missing: list[str] = []
            if not scenario.given:
                missing.append("Given")
            has_full_interaction = any(i.when and i.then for i in scenario.interactions)
            if not has_full_interaction:
                if not scenario.when_clauses:
                    missing.append("When")
                if not scenario.then_clauses:
                    missing.append("Then")
            if missing:
                yield self.violation(
                    f"Scenario {scenario.name!r} is missing required phase(s): "
                    f"{', '.join(missing)}",
                    location=self.loc(scenario, f"scenario {scenario.name!r}"),
                    severity="error",
                )
