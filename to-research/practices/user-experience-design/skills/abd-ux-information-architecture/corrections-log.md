# abd-information-architecture — corrections log

Log entries follow the workspace `correct-output` rule format. Each entry stays attached to the skill that produced the wrong output, not to chat history.

---

### Left-panel chrome stacked above body instead of beside it

- **DO:** Use `add-chrome <screen> <region> --panel left` for any chrome region the real UI places beside the content area (crowd tree, sidebar, nav panel). The CLI renders it as a left column alongside body (list/form) regions.
- **DO NOT:** Call `add-chrome` without `--panel left` for a panel — this stacks it full-width above the list, which never matches a real left-panel + body layout.
- **Example (wrong):** `add-chrome "crowd manager — identities" "crowd tree"` → crowd tree rendered full-width above identity list, crowd tree and identity list stacked vertically.
- **Example (correct):** `add-chrome "crowd manager — identities" "crowd tree" --panel left` → crowd tree rendered as left column, identity list beside it on the right.
- **Likely source:** `automation gap` — CLI had no left-panel concept; all `add-chrome` calls produced full-width bands.
- **Status:** confirmed

---

### Grey used indiscriminately on data rows

- **DO:** Apply grey (`fillColor=#f5f5f5 / strokeColor=#cccccc`) only via `--dimmed` on chrome regions that repeat unchanged across sibling tab screens. This signals "same as primary screen."
- **DO NOT:** Apply grey style to list rows or form field rows. Data rows are content, not repeated chrome, and carry no grey style.
- **Example (wrong):** `S.row` and `S.formRow` styles used `strokeColor=#cccccc` — every data row in every screen was grey-bordered.
- **Example (correct):** `S.row` and `S.formRow` use `strokeColor=none` — rows have no border. `S.chromeDimmed` (`fillColor=#f5f5f5`) is reserved for `--dimmed` chrome on sibling screens.
- **Likely source:** `prompt gap` — no rule distinguished grey-for-repetition from grey-for-data-rows.
- **Status:** confirmed

---

### Empty chrome boxes added with no content

- **DO:** Only add a chrome region (toolbar, footer, sidebar) if it has visible content at IA level — named items, labelled structure, or a panel with a tree/list.
- **DO NOT:** Add an empty named chrome box (e.g. `toolbar` with nothing in it). An empty box adds noise, suggests incomplete layout, and was shown in the reference as `(chrome — no actions)` which is now removed.
- **Example (wrong):** `add-chrome "crowd manager — identities" "toolbar"` and `add-chrome "crowd manager — abilities" "toolbar"` added empty italic boxes with no content on every screen.
- **Example (correct):** Toolbar omitted. Only chrome with visible IA-level content is added.
- **Likely source:** `prompt gap` — reference example explicitly showed `toolbar (chrome — no actions)` which canonised the empty-box pattern.
- **Status:** confirmed
