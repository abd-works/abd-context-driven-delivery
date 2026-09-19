# PracticeGuidance

- Join Clean Engineering companion instructions from **`PracticeGuidance.clean_engineering_companion.instructions`**. That property is the companion for the current fidelity. Fidelities read **`self.clean_engineering.instructions`**. Do not add `ce()`, `companion_instructions()`, or re-join companion text in a subclass `guidance`.
- Use **`PracticeGuidance.render`**. Set `_formats`. Do not copy parse/render onto the practice.
- Put every format adapter under `{practice}/model/{format}/`. Canonical types live in `model/`. Do not add `document/`, `diagram/`, `code/`, `web/`, or a named `{practice}_model` package beside `model/`.
- **`Guidance.tools` includes `@Hook` members.** Install walks `tools`; if `inject_rules` is omitted, chat edits never enroll and no practice rules load.
- **`PracticeGuidance.inject_rules` walks shared rules and every fidelity glob.** Shared CE rules have no file globs; code lives on the code fidelity (`**/*.py`). Matching only `self.rules` on the practice injects nothing for a catalog Python edit.
- **Name Guidance, a toolset, an operation, a tool, or instructions — not a host.** MCP host and hook server keep those names. Do not use host as a stand-in for any of the agent types.
- **Skill and MCP copy for `instructions` is `overview`.** Do not fall back to the guidance section, and do not add a `prompt_message` property.
- **Keep helpers on the class that uses them.** `domain_slug` lives on `PracticeGuidance`. Hook path matching and toast labels live on `Guidance` as instance methods. Do not add module-level functions or `@staticmethod` for work that always runs on an instance.
