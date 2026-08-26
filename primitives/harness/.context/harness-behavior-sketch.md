Fidelity: behavior

**Sources / context:** this chat; issue 7 (names, aliases, operation annotations, rules).

What changed: batch from agent_skills — name filter; scaffold as its own action; full tool fidelity slugs including CE/DDD/UX; echo/handoff prompts; no disable-model-invocation; clean needs @prompt; state beside Harness. ActionBody stays as sketched.

**Refactor these tests:**
- `context_tools/base/base_context_tool_spec.py` — generate / validate / satisfy / document / render / createRule / host turn tools
- `context_tools/actions/workspace/workspace_session_spec.py` — generate composer
- `context_tools/actions/workspace/workspace_spec.py` — host begin_turn / finish_turn / record_* face; keep Workspace stories
- `context_tools/actions/sketch/sketch_spec.py` — merge sketch_session into sketch
- `context_tools/actions/iterate/iterate_spec.py` — merge iterate_session into iterate
- `context_tools/actions/grill_context/grill_context_spec.py` — merge grill_with_context into grill
- `context_tools/actions/partition/partition_spec.py` — merge partition_corpus into partition

a harness
  -> harness = new Harness(type)
  that is created
    with no type given
      it should refuse
        -> expect(lambda: Harness()).to raise_error
  that generates
    with no IDE given
      it should AskQuestion for the IDE
        -> expect(harness.generate).to ask "Which IDE?"
      -> harness = new Harness(type)
    with no name filter given
      it should AskQuestion all or a substring
    with no source
      it should walk the workspace
      it should generate each source into the deploy area
      it should write a Harness skill
      it should write a Harness prompt
      it should not be a separate deploy
      it should not confirm the scanned list
      it should overwrite generated files
      it should remove stale shortcuts and old slugs
      it should save the IDE
    with a source
      it should write that source into the deploy area
    with a context toolset
      -> skill = new Skill(type)
      -> skill.generate(contextToolset)
      it should add that skill
        -> expect(harness.skills).to contain skill
      it should write one file for the whole context tool
      it should not add a skill per inner tool
      it should use the context-tool body
        -> expect(skill.body).to equal ContextToolBody.from(contextToolset)
    with a utility toolset
      -> skill = new Skill(type)
      -> skill.generate(utilityToolset)
      it should add that skill
      it should use the context-tool body
    with an action
      -> prompt = new Prompt(type)
      -> prompt.generate(action)
      it should add that prompt
        -> expect(harness.prompts).to contain prompt
      it should name the prompt from the package
      it should generate from the merged agent_instructions
        -> expect(prompt.body).to equal ActionBody.from(action)
      with type Cursor
        it should deploy as a command
    with a slash companion
      -> prompt = new Prompt(type)
      -> prompt.generate(companion)
      it should add that prompt
      it should use the action body
    with echo
      it should write a prompt
    with handoff
      it should write a prompt
    with scaffold
      -> prompt = new Prompt(type)
      -> prompt.generate(scaffold)
      it should add that prompt
      it should use the action body
      it should not treat scaffold as a fidelity
    with a format
      -> prompt = new Prompt(type)
      -> prompt.generate(format)
      it should add that prompt
      it should use the format body
        -> expect(prompt.body).to equal FormatBody.from(format)
      it should tell the agent to run using that format
      it should name generate and render
      it should not set a fidelity
    with a CDD stage fidelity
      -> prompt = new Prompt(type)
      -> prompt.generate(stage)
      it should add that prompt
    with a tool-specific fidelity
      -> prompt = new Prompt(type)
      -> prompt.generate(fidelity)
      it should add that prompt
    with CleanEngineering model
      it should write a model prompt
    with DDD bounded_context
      it should write a bounded_context prompt
    with UX ia
      it should write an ia prompt
    with @skill, @prompt, or @instruction on the operation
      it should write that file kind instead of the default skill or prompt
    with @skill and @prompt on the operation
      it should write a skill and a prompt
    with @skill(name) on the operation
      it should use that name
        -> expect(tool.name).to equal skill.name
    with type Cursor
      it should write under .cursor/
    with type VS Code
      it should write under .github/
    with type Claude
      it should not implement yet
    with type Codex
      it should not implement yet
    with type ChatGPT
      it should not implement yet

a generated harness tool
  that generates
    with a context tool given
      it should not require an action
      it should lead with guidance clustering
        -> expect(tool.description).to equal contextTool.overview
      it should include the class string
      with attached operation instructions
        it should generate with those operation instructions
      with a skill file
        it should use the context-tool body
      with a command file
        it should use the context-tool body
    with an action given
      it should not require a context tool
      it should include the class string
      it should include this operation's instructions
      with provided context tools
        it should run this action for those context tools
      with no context tool provided
        it should run on the context in general
      with a skill file
        it should use the action body
      with a command file
        it should use the action body
    with qualitative guidance or an action taken from the context
      it should confirm
        -> expect(tool.body).to contain "confirm"
    with a fidelity that does not belong to the in-scope tool
      it should guess the correct fidelity
      it should confirm
    with neither qualitative guidance nor an action available
      it should AskQuestion
        -> expect(tool.body).to contain "AskQuestion"
      it should constrain AskQuestion to this source
    with the action specified
      it should not require it from the context
      it should put the CLI after that
        -> expect(tool.body).to contain "python -m tools run"

a skill
  -> skill = new Skill(type)
  that generates
    with a context toolset given
      it should write a SKILL.md from that toolset
    with type Cursor
      it should write .cursor/skills/{name}/SKILL.md
    with type VS Code
      it should write .github/skills/{name}/SKILL.md
    it should not set disable-model-invocation

a command
  -> command = new Command(type)
  that generates
    with a prompt on Cursor
      it should write .cursor/commands/{name}.md

a prompt
  -> prompt = new Prompt(type)
  that generates
    with @prompt on the operation
      it should write a prompt file
    with type VS Code
      it should write .github/prompts/{name}.prompt.md
    with type Cursor
      it should deploy as a command
        -> command = new Command(type)
        -> command.generate(source)
      it should write .cursor/commands/{name}.md

an instruction
  -> instruction = new Instruction(type)
  that generates
    with @instruction on the operation
      it should write an instruction file
    with type VS Code
      it should write .github/instructions/{name}.instructions.md
    with type Cursor
      it should deploy as a rule
        -> rule = new Rule(type)
        -> rule.generate(source)
      it should write .cursor/rules/{name}.mdc

a rule
  -> rule = new Rule(type)
  that generates
    with an instruction on Cursor
      it should write .cursor/rules/{name}.mdc

a context tool
  that runs guidance
    it should include contexts
    it should include examples
    it should include templates
  that runs generate
    it should run Generate
  that runs validate
    it should run Validate
  that runs document
    it should run Document
  that runs satisfy
    it should run Satisfy
  that runs render
    it should run Render

Generate
  -> generate = new Generate()
  that runs
    with one context tool
      it should run on that context tool
      it should run that context tool's guidance
    with two context tools
      it should run on each context tool
    with a CarChronicle
      it should inline the full Contexts section from car_chronicle.md
      it should inline the full examples.md file
      it should inline the full car_chronicle templates file
      it should not inline meta contexts from create_context_tool.md
      it should inline generate prose
      it should require several turns for a large implied source even if asked once
      it should include generate_output, generate_fixes_from_validate, and add_generate_header in generate

Validate
  -> validate = new Validate()
  that runs
    with one context tool
      it should run on that context tool
      it should run that context tool's guidance
    with two context tools
      it should run on each context tool
    with a CarChronicle
      it should inline the full Contexts section as rubric
      it should name scan then finish_turn
      it should inline validate prose

CreateRule
  -> createRule = new CreateRule()
  that runs
    with one context tool
      it should run on that context tool
      it should run that context tool's guidance
    with two context tools
      it should run on each context tool
    with a CarChronicle
      it should set action to createRule
      it should inline the createRule guide

Document
  -> document = new Document()
  that runs
    with one context tool
      it should run on that context tool
      it should run that context tool's guidance
    with two context tools
      it should run on each context tool
    with a CarChronicle
      it should inline document prose

Satisfy
  -> satisfy = new Satisfy()
  that runs
    with one context tool
      it should run on that context tool
      it should run that context tool's guidance
    with two context tools
      it should run on each context tool
    with a CarChronicle
      it should name validate then generate_fixes_from_validate then finish_turn
      it should inline satisfy prose
      it should not inline the domain template in tool mode

Render
  -> render = new Render()
  that runs
    with one context tool
      it should run on that context tool
      it should run that context tool's guidance
    with Stories
      it should render already-generated markdown into json via transform
    with CleanEngineering
      it should render already-generated markdown into json via transform
    with Ux
      it should render already-generated json into markdown via transform
    with an unsupported format
      it should reject

agent guidance
  // later

agent
  // later

hook
  // later

Iterator / Workspace / Turn are unchanged except the merges below — not re-sketched here.

Sketcher
  that runs sketch
    it should include the sketch_session body in sketch

Iterator
  that runs iterate
    it should include the iterate_session body in iterate

GrillContext
  that runs grill
    it should include the grill_with_context body in grill

Partition
  that runs partition
    it should include the partition_corpus body in partition

Workflow
  that runs backlog
    it should include the handoff_tool body in backlog

agent skills
  that is replaced by a harness
    it should not remain the deploy owner
    it should be deleted

generateAgain
  -> harness.generateAgain()
  that runs
    with saved state
      it should not AskQuestion
      it should write using the saved IDE
    with no saved state
      it should refuse

clean
  -> harness.clean()
  that runs
    with @prompt on the operation
      it should write a prompt
    with type Cursor
      it should clean that Cursor deploy area
      it should not clean VS Code
