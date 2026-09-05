# Rule: Only in-scope domain terms may appear as control labels

Control labels in the wireframe and `mockup.md` must use domain terms that belong to the stories in scope for this pass. Terms from other screens or stories not in scope must not appear as labels.

**DO** build the term set from the in-scope story list, intersected with the domain terms file.

**DO NOT** label a control with a term whose story is not in scope for this pass, however relevant it seems.

**Example (pass):** The game directory prompt covers *Validate City of Heroes Game Directory* and *Prompt for Game Directory if Invalid*. These reference `COH game directory`. The input label is `COH game directory`.

**Example (fail):** Labelling an input `crowd repository path` — the crowd repository is referenced by the story but the term belongs to the crowd manager screen, not the game directory prompt.

**Example (fail):** Including a full domain term legend beside the wireframe. The wireframe reads like the screen, not like the domain terms file.
