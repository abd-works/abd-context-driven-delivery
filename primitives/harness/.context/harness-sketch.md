Fidelity: model

**Sources / context:** this chat; issue 7 (names, aliases, operation annotations, rules); `utilities/agent_skills/agent_skills.py` write paths.

What changed: batch from agent_skills — name filter; scaffold as its own action; full tool fidelity slugs including CE/DDD/UX; echo/handoff prompts; no disable-model-invocation; clean needs @prompt; state beside Harness. ActionBody stays as sketched.

primitives/
  tools
  actions
       // new: Generate, Validate, Document, Satisfy, Render
       // new in Validate package: CreateRule
  instructions
  focus
  harness
    -> Harness.generate
       // python -m tools manifest harness.harness:Harness
       // python -m tools run _req.yaml
       // same two commands as grill, sketch, agent_skills — not a new kind of thing
       // python -m tools manifest harness.harness:Harness
       // python -m tools run _req.yaml
       // same CLI as every other agentic operation — replaces agent_skills
  context_tools
       // one @agent_instructions — guidance: contexts, examples, templates
       // no generate / validate / document / satisfy / render

Harness
  // @agentic_toolset
  // python -m tools manifest harness.harness:Harness
  type
       // must be given at construction
       // Cursor | VS Code implemented now
       // Claude | Codex | ChatGPT named, not implemented
  commands
  prompts
  instructions
  skills
  agents
       // later
  hooks
       // later
  agentGuidance
       // later
  generate
       // @agent_instructions
       // @skill @prompt — later runs are the skill or /harness
       with no IDE given
         // AskQuestion: which IDE? Cursor | VS Code
         -> harness = new Harness(type)
       with no name filter given
         // AskQuestion: all toolsets (recommended) / enter a substring
       with no source
         // first run is the two CLI commands
         // walk context_tools/ and utilities/ like agent_skills.scan_toolsets
         // then generate each source into the deploy area
         // also write Harness itself — skill and prompt (not in that walk)
         // later runs: the skill or /harness
         // skills, commands, formats, fidelities, companions — one operation
         // generate is the deploy — no separate deploy
         // no confirm list
         // overwrite generated files
         // remove stale shortcuts and old slugs — same as agent_skills
         // save last IDE
       with a source
         // write into the deploy area — .cursor/ or .github/
       with a context toolset
         -> skill = new Skill(type)
         -> skill.generate(contextToolset)
         // one skill for the whole context tool
       with a utility toolset
         -> skill = new Skill(type)
         -> skill.generate(utilityToolset)
       with an action
         -> prompt = new Prompt(type)
         -> prompt.generate(action)
         // default is prompt (VS Code name)
         // Cursor has no prompt files — deploy as a command
       with a slash companion
         -> prompt = new Prompt(type)
         -> prompt.generate(companion)
         // echo, handoff, backlog, start, finish
       with scaffold
         -> prompt = new Prompt(type)
         -> prompt.generate(scaffold)
         // separate action — not a fidelity
         // ActionBody
       with a format
         -> prompt = new Prompt(type)
         -> prompt.generate(format)
         // not a fidelity
         // hardcoded for now — CleanEngineering + Stories channels
         // markdown, json, drawio, miro, python, typescript, java, javascript
         // body: run the context tool / actions using the following format: {format}
         // mostly generate and render
         // Cursor has no prompt files — deploy as a command
       with a CDD stage fidelity
         -> prompt = new Prompt(type)
         -> prompt.generate(stage)
         // discovery, specification, engineering
       with a tool-specific fidelity
         -> prompt = new Prompt(type)
         -> prompt.generate(fidelity)
         // hardcoded from each tool's fidelities table
         // Stories: story_map, scenarios, acceptance_tests
         // DDD: bounded_context, building_blocks, tactics
         // CleanEngineering: modules, model, specification, code
         // UX: ia, mockup, front_end_code
         // BDD: modules, behavior, development
         // CDD: spec, engineer
       with @skill, @prompt, or @instruction on the operation
         // VS Code names only — no Cursor-specific decorators
         // @prompt from Prompt; @instruction from Instruction; @skill from Skill
         // Cursor: @prompt deploys as a command; @instruction deploys as a rule
         // write that file kind instead of the default skill / prompt
         // several decorators on one operation — write each
         // unannotated sources still get the default write
         // body still follows source kind
         // body includes class string and the merged operation instructions
       with type Cursor
         // each tool writes under .cursor/
         // multi-folder workspace: also ~/.cursor and workspace-parent .cursor — same as agent_skills
       with type VS Code
         // each tool writes under .github/
       with type Claude or Codex or ChatGPT
         // must not implement yet
  generateAgain
       // @agent_tool
       // no questions
       // last IDE from saved state
       // state file beside the Harness package
       with no saved state
         // refuse
  clean
       // @agent_tool
       // @prompt — override so generate knows the file kind
       // this type's deploy area only — not both IDEs

  ----
 HarnessType
      Cursor
      VS Code
      Claude
      Codex
      ChatGPT

  ----
 BaseContextTool
      guidance
           // one @agent_instructions
           //    self.contexts
           //    self.examples
           //    self.templates
      // drop generate, validate, document, satisfy, createRule
      // drop generate_output, generate_fixes_from_validate, add_generate_header_to_generated
      // drop scan, render
      // drop begin_turn, finish_turn, record_mistake, record_correction

  ----
 Generate
      generate(tools)
           // runs on each provided context tool
           // that tool's guidance (contexts, examples, templates)
           // merge generate_output, generate_fixes_from_validate, add_generate_header_to_generated into this operation

  ----
 Validate
      validate(tools)
           // runs on each provided context tool
           // scan then finish_turn

  ----
 CreateRule
      // new action in the Validate package
      createRule(tools, failed, wanted)
           // runs on each provided context tool

  ----
 Document
      document(tools, paths)
           // runs on each provided context tool

  ----
 Satisfy
      satisfy(tools)
           // runs on each provided context tool
           // validate then generate_fixes then finish_turn

  ----
 Render
      render(tools, format, content)
           // runs on each provided context tool

  ----
 Sketcher
      // modified — merge sketch_session into sketch
      sketch(tools)
  ----
 Iterator
      // modified — merge iterate_session into iterate
      iterate(tools)
  ----
 GrillContext
      // modified — merge grill_with_context into grill
      grill(tools)
  ----
 Partition
      // modified — merge partition_corpus into partition
      partition(tools, context)
  ----
 Workflow
      // modified — merge handoff_tool into backlog
      backlog
      // start / finish stay @agent_tool

  ----
 HarnessTool
      // decorator on the operation — VS Code names only: @skill from Skill, @prompt from Prompt, @instruction from Instruction
      // no @command or @rule — those are Cursor equivalents written at generate time
      type
      name
           // optional deployed name on the decorator; default is the package / module slug
           // no aliases
      description
           // autocomplete tooltip — most concise first
      body
           // filled from source kind (ContextToolBody | ActionBody | FormatBody)
      generate source
           // source is the context tool or the action

  ----
 Resolve
      // an action does not require a context tool
      // a context tool does not require an action
      // take qualitative guidance from the context when it is there
      // take the action from the context and/or from what was specified
      // if you got it from the context: confirm
      // if the fidelity does not belong to the in-scope tool: guess the correct one and confirm
      // if you cannot get guidance and cannot get the action: AskQuestion
      //      constrained list baked from this source

  ----
 ContextToolBody
      // same recipe whether the file is a skill or a command
      // does not require an action
      // 1. guidance clustering (overview) — tooltip first
      // 2. class string — class-level documentation
      // 3. operation instructions — guidance
      // 4. Resolve
      // 5. then the CLI required to run — unchanged
      //      python -m tools manifest {toolset}
      //      python -m tools run _req.yaml

  ----
 ActionBody
      // already locked — do not port the agent_skills kit-owned / chain-tools recipe
      // same recipe whether the file is a skill or a command
      // does not require a context tool
      // 1. run this action for any provided context tools, or on the context in general
      // 2. class string
      // 3. this operation's instructions — the merged @agent_instructions
      // 4. Resolve
      // 5. then the CLI required to run

  ----
 FormatBody
      // not a fidelity
      // run the context tool / actions using the following format: {format}
      // mostly generate and render

  ----
 Skill : HarnessTool
       // @skill
       // no disable-model-invocation
       // Cursor: .cursor/skills/{name}/SKILL.md
       // VS Code: .github/skills/{name}/SKILL.md
       generate source

  ----
 Command : HarnessTool
       // not a decorator — Cursor write for @prompt
       // Cursor: .cursor/commands/{name}.md
       generate source

  ----
 Prompt : HarnessTool
       // @prompt
       // VS Code: .github/prompts/{name}.prompt.md
       // Cursor has no prompt files — deploy as a command
       generate source

  ----
 Instruction : HarnessTool
       // @instruction
       // VS Code: .github/instructions/{name}.instructions.md
       // Cursor has no instruction files — deploy as a rule
       generate source

  ----
 Rule : HarnessTool
       // not a decorator — Cursor write for @instruction
       // Cursor: .cursor/rules/{name}.mdc
       generate source

  ----
 Hook : HarnessTool
       // later
       generate source

  ----
 Agent : HarnessTool
       // later
       generate source

  ----
 AgentGuidance : HarnessTool
       // later
       generate source
