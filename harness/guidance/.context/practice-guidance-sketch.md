fidelity: model
scope: PracticeGuidance format, CE companion, render folders
status: agreed — formal model in practice-guidance-model.py / .md

=========
theme: default format
---------
ce:
PracticeGuidance : Guidance
  fidelities
  format
  load_fidelities_from_markdown
       -> fidelity_blocks
       -> FidelityGuidance
  // never _fidelity_format_defaults
  // constructor format overrides FidelityGuidance.default_format
  // omitted format → current fidelity default_format

  ----
FidelityGuidance : Guidance
  name
  stage
  default_format
  practice_guidance
  // stage from **Stage:**; default_format from **Default format:** in the same block

  ----
Markdown
  fidelity_blocks text
  fidelity_stage body
  fidelity_format body
       // same extract pattern as fidelity_stage
       // first token is the channel name (markdown, python, drawio, html, …)
       // // unresolved: prose values like "project language" / "Python" casing

=========
theme: clean engineering companion
---------
ce:
FidelityGuidance : Guidance
  clean_engineering
  // optional FidelityGuidance on CleanEngineering; null → skip
  // **Clean Engineering:** {modules|model|code}; omit → null
  // never ce() on PracticeGuidance; never required

PracticeGuidance : Guidance
  guidance
       -> fidelities.current
            -> // if clean_engineering is null, skip
            -> clean_engineering.instructions
  load_fidelities_from_markdown
       -> fidelity_clean_engineering body
            -> // resolve name against CleanEngineering.fidelities; miss → null

  ----
Markdown
  fidelity_clean_engineering body
       // same extract pattern as fidelity_stage; empty → null

=========
theme: render
---------
ce:
{practice}/
  model                              <-- canonical types (StoryMap, UxMap, CleanEngineeringModel)
    markdown
    json
    drawio
    miro
    python
    html                             <-- only formats that practice actually has
  // format folders nest under model/; never document/ diagram/ code/ web/
  // bdd/ and ddd/ have no model or format folders

Render : GuidanceAction
  render guidance format content
       -> PracticeGuidance.render format content

PracticeGuidance : Guidance
  formats
  render format content source
       -> // no formats and current.clean_engineering set → that practice.render
       -> formats[source or self.format].parse content
       -> formats[format].render model
  // one loop; _CHANNELS dicts go away; Render action does not grow transformers

  ----
markdown
  parse content
  render model
  // same pair in every format folder; extras (miro upload, drawio keep_positioning) stay here




=========
theme: interaction flow
---------
ce:
clean-engineering-model (Skill)
  // agent already has the python model artifact; conversion starts here
  -> render (Skill)
       -> McpServer.invoke_tool render.render
            -> Render.render guidance format content
                 -> GuidanceAction.run guidance
                      -> begin action="render"
                           -> Workspace.open
                           -> Turn.action
                           -> RecordDecisions.record_decisions_session
                      -> listed
                           -> AgentToolSet.instantiate_all
                                -> CleanEngineering fidelity="model"
                      -> each host
                           -> CleanEngineering.render format="drawio" content
                                -> fidelities.current
                                     -> // default_format python unless constructor format was passed
                                -> formats[source or self.format].parse content
                                     -> python.parse content
                                          -> CleanEngineeringModel
                                -> formats[format].render model
                                     -> drawio.render model
                                          // keep_positioning / previous stay in drawio/
                      -> end
                           -> Turn.turn

  ----
bdd-behavior (Skill)
  // no model/{format}/ on BDD — companion supplies render
  -> render (Skill)
       -> Render.render guidance format content
            -> Bdd.render format content
                 -> fidelities.current.clean_engineering
                      // null → skip (no conversion)
                      -> practice_guidance.render format content
                           -> // same CleanEngineering loop as above

