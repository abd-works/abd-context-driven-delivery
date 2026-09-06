# Handoff - BaseContextTool split bout closed

## 1. Next session focus

**Bout closed.** BaseContextTool split (modules→model) is done: kits extracted, layout verified, concept-owned instruction slots on kits, `context_tool_spec` 38/38. Next work is outside this bout — pick the next CleanEngineering fidelity/scope, or commit the split if that is the next human step.

## 2. Resume in three lines

(a) Stage: **model extract + post-extract verify complete** — bout `context-tool-split` on `context_tools/base`; fidelities modules→model.
(b) Last accepted: MI composer; kits under `utilities/` + `artifact_lifecycle` under base; instruction ownership = concept kit (`partition_guidance`→PartitionPipeline; generate/document/examples/templates→BaseContextTool; composer keeps `module_dir`+`contexts`); duplicate `segment_named_entry_completeness` removed; grill Folder layout / Scan kit home cleaned.
(c) Next: do not re-open module cut; choose next CE fidelity or land the working tree.

## 3. Generator state

- Toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering (via BaseContextTool)
- Bout: context_tools/base/.context/sessions/context-tool-split/ (closing)
- Modules sketch: context_tools/base/.context/sessions/context-tool-split/context-tool-modules-sketch.md
- Build order: context_tools/base/.context/module-build-order.md (1–6 done)
- Composer: context_tools/base/context_tool.py (thin: module_dir + contexts + @base_context_tool)
- **context_index_path:** .context/context-index.md
- **Current tool=root:** clean_engineering = ./context_tools/base/*

## 4. Grilling / skills state

- Grill answers: context_tools/base/.context/sessions/context-tool-split/grill-answers.md
- Headings: Composer shape; Module cut; Workspace + session; Scan naming; Repair vs log_fix; Peer dependencies; Engagement engines; Folder layout; Scan kit home; Engagement wrappers home; Model / extract
- Process locks:
  - Composer merge, not facade; no DomainContent module
  - Instructions that belong to a concept live on that concept's kit (merge brings them in)
  - Composer shared domain face only: module_dir, contexts, @base_context_tool
  - Workspace+session = one kit; scanners kit in utilities/scanners
  - Peers have no kit→kit deps; only composer depends on kits
  - log_fix + repair same kit; concrete classes only; BaseContextTool CT-only under base/
- Suggested skills: next CE bout create_session / generate for next fidelity; commit only if user asks

## 5. CDD progress

None (no cdd-sketch in this bout).

## 6. Artifacts to read

- .context/context-index.md (Current: clean_engineering = ./context_tools/base/*)
- context_tools/base/.context/sessions/context-tool-split/grill-answers.md
- context_tools/base/.context/sessions/context-tool-split/context-tool-modules-sketch.md
- context_tools/base/.context/module-build-order.md
- context_tools/base/context_tool.py
- Kit homes: utilities/workspace_session/, utilities/scanners/, utilities/partition_pipeline/, utilities/repair/, context_tools/base/
- Spec: context_tools/base/context_tool_spec.py (38/38)

## 7. Open questions / risks

- Working tree has many unrelated sandbox deletions / other edits mixed with the split — separate commit scope carefully if landing.
- Broader domain-spec regression (stories/CE/agent_bdd suites) not fully re-run this close; context_tool_spec + scanner specs green.
- context_tool.md favour-defaults prose may still say instruction slots live on BaseContextTool framework generally — true for domains (do not override); kit ownership is the split detail.
