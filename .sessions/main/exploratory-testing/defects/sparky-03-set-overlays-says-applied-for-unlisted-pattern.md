# sparky-03: graph.set_overlays says it applied a pattern the project does not use, or another project's pattern

**Title** - `graph.set_overlays` answers "Applied pattern overlays: <name>." and keeps the name in `overlays` for a pattern the project's list leaves out, for a name that is no pattern at all, and for another project's own pattern folder, although none of their rules is applied.

**Charter** - Sparky, theme 1. **Tester** - Sparky.

**Story** - no scenario covers this. CDR 0005: "A pattern no list names is left out of installs, the server's tools, and overlay choices"; `Session.choose_overlays` refuses such a name with `NotAPatternError`, but the graph tool does not.

**Module and class** - `harness/graph/pattern_overlays.py` `PatternOverlays.apply` / `_paths_of` / `root_of` (an unknown name falls through to `Path(overlay).resolve()`, a folder under the server's own checkout; any folder holding `practices/` is taken as given, whatever project it belongs to), and the message the graph toolset builds from `paths` rather than from `patterns`.

**Severity** - misleading message.

**Steps** (server and projects as in sparky-01/02; alpha lists `["stories", "ddd", "lern_domain_driven"]`, beta has no list and its own `lern_domain_driven`)
1. `X-CDD-Project: .../work/alpha`, `graph.set_overlays {"overlays": ["mern_domain_driven"]}`.
2. Same, `{"overlays": ["nonsense_pattern"]}`.
3. Same, `{"overlays": ["<build>/cdd_guidance/patterns/mern_domain_driven"]}`.
4. `X-CDD-Project: .../work/beta`, `graph.set_overlays {"overlays": ["C:/dev/_et/after-1-2-1/sparky/work/alpha/guidelines/alpha_domain_driven"]}`.

**Expected** - Each is refused, or answered as not applied, naming the patterns the project can use (`available_overlays` already lists them: alpha `['lern_domain_driven']`, beta `['cdd_claude_mod', 'cdd_web_domain_access', 'lern_domain_driven']`).

**Actual**
- 1: `Applied pattern overlays: mern_domain_driven.`, `overlays` = `['C:\...\nostalgic-mclaren-b1ae7c\mern_domain_driven']` (a folder that does not exist, under the server's checkout, not the project).
- 2: `Applied pattern overlays: nonsense_pattern.`, same kind of path.
- 3: `Applied pattern overlays: mern_domain_driven.`; no `mern` rule appears in the inventory.
- 4 (beta): `Applied pattern overlays: alpha_domain_driven.`, `overlays` holds alpha's folder.
The rules are rightly not applied, so the project's patterns do not leak, but the person or agent is told they were.

**Tier that should catch it** - unit (`harness/graph/project_patterns_spec.py`: apply a name the project does not list and check the answer). The specs check what is applied, not what the answer says.
