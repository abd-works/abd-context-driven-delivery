fidelity: model
scope: PracticeGuidance.fidelities as @markdownCollection -> GuidanceCollection
status: grill cycle — review before more questions

=========
theme: bind the bag; selected stays on it; load is from_markdown
---------
ce:
PracticeGuidance : Guidance
  @markdownCollection("fidelities") fidelities : GuidanceCollection
       // first-class nested toolset — nested_toolsets is this object
  instructions
       -> super.instructions
       -> fidelities.markdown
       // proposed join — see miss below vs today tools(child.instructions)
  fidelityInstructions name
       -> fidelities[name].instructions
       // MCP by name; not the same as selected
  ----
 GuidanceCollection : ToolSetCollection, Guidance
  parent
  entries
  current
  stage
  markdown
       // keep_extract of ## Fidelities — original section, not join of child.instructions
  from_markdown text
       -> Markdown.fidelity_blocks
       -> FidelityGuidance
       -> bind_yaml
       // EXTEND coerce: return type GuidanceCollection, not key-value map
  ----
 FidelityGuidance : Guidance
  name
  stage
  default_format
  practice_guidance
  instructions
       // still assembled: practice parent + own overview/guidance/rules + templates + CE

=========
theme: what this unlocks
---------
ce:
// attach_fidelities gone — collection.bind(practice) holds the bag
// load_fidelities_from_markdown body moves to GuidanceCollection.from_markdown
// selected / current already on the collection; activate sets it
// ToolSetCollection does not load markdown — only GuidanceCollection.from_markdown

=========
theme: what you are missing
---------
ce:
// 1. today tools(fidelity.instructions) defers each child's assembled MCP instructions;
//    fidelities.markdown is the raw ## Fidelities extract. Replacing the loop with
//    + fidelities.markdown inlines raw section text and drops the tools() list.
// 2. FidelityGuidance.instructions != collection.markdown (parent prose, templates, CE).
// 3. @markdownCollection getter coerces, then collection.bind(instance) — later
//    reads return that same bag so current stays. No attach_fidelities.
// 4. CE companion wiring is after load; not generic coerce.
// 5. fidelityInstructions(name) still needed for MCP give-me-sketch; selected is activate.
