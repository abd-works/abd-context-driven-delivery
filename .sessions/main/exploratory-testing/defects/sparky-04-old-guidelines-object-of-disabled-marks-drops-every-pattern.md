# sparky-04: an old-style guidelines object that only marks patterns disabled leaves the project with no pattern at all

**Title** - A `.context/config.json` written by an earlier CDD, whose `guidelines` object marks some patterns `disabled` and names no others, is read as an empty list, so the project loses every pattern, including the ones it never disabled (`lern_domain_driven`, `cdd_web_domain_access`, `cdd_claude_mod`).

**Charter** - Sparky, theme 1. **Tester** - Sparky.

**Story** - no scenario covers this. CDR `harness/graph/.context/cdr/0005-a-project-keeps-its-own-patterns.md`, Consequences: "A `guidelines` object an earlier CDD wrote, marking each `enabled` or `disabled`, is read as the list of the ones it marks `enabled`, so projects keep working until their config is rewritten as a list." Commit d58373b13 (the day's first version) wrote: "any guideline the config marks disabled is left out" - i.e. an object of `disabled` marks meant "every pattern but these". Before d58373b13 an unnamed pattern was served, installed and offered as an overlay in every project.

**Module and class** - `harness/installation/context_config.py` `ContextConfig.guidelines` (a Mapping becomes the list of names marked `enabled`, so an object of only `disabled` marks becomes `[]`, which `ProjectGuidelines.uses` treats as a list naming nothing rather than as no list). Also a value of JSON `true` is not read as enabled.

**Severity** - wrong result (question on intended reading: should an object with no `enabled` mark fall back to CDD's list less the disabled ones?).

**Steps**
1. Server as in sparky-01 (`python -m harness.mcp --port 8911`).
2. Project `work/legacy` (git repo) with `.context/config.json` = `{"guidelines": {"mern_domain_driven": "disabled", "oss_portal_domain_driven": "disabled"}}`.
3. `tools/list` with `X-CDD-Project: C:/dev/_et/after-1-2-1/sparky/work/legacy`, filter names containing `domain` or `claude-mod`.
4. In process: `HeldProjectGuidelines().of(<project>).chosen(REGISTERED_PATTERNS.classes)` for `{"guidelines": {"mern_domain_driven": "disabled"}}` and for `{"guidelines": {"lern_domain_driven": true}}`.

**Expected** - The project keeps working as it did: the patterns it did not disable (`lern_domain_driven`, and CDD's listed ones) are served, installed and offered; only `mern_domain_driven` and `oss_portal_domain_driven` are left out.

**Actual** - 290 tools, none of `lern-domain-driven.instructions`, `cdd-web-domain-access.instructions`, `cdd-claude-mod.instructions` (a project with no config at all gets 293 with all three). In process both configs choose `[]`. The installer, overlay choices and graph read the same `ProjectGuidelines`, so an install into such a project drops those patterns too.

**Tier that should catch it** - unit (`harness/installation/context_config_spec.py` / `project_guidelines_spec.py`). The spec for the old object covers a mix of `enabled` and `disabled` marks, never one with no `enabled` mark.
