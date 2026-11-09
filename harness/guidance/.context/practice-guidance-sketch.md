fidelity: model / behavior
scope: PracticeGuidance format, CE companion, render folders
status: ce model agreed; bdd behavior signatures in practice_guidance_behavior_spec.py
// built: the current classes are in practice-guidance-model.md; names below follow the code

=========
theme: default format
---------
ce:
PracticeGuidance : Guidance
  fidelities
       // @markdownCollection: MarkdownCollection.coerce reads the Fidelities section
       -> Markdown.fidelity_blocks
       -> FidelityGuidance
  format
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
  fidelities
       -> Markdown.fidelity_clean_engineering body
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
       -> // object model content → skip parse
       -> // tool content → instantiate model from that tool's context
       -> // code layer → formats[python|typescript|java|javascript].parse tree, never markdown
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
            -> Render.render guidance format paths
                 -> _work_on guidance
                 -> load_document content paths
                 -> each
                      -> listed
                           -> AgentToolSet.instantiate
                                -> CleanEngineering fidelity="model"
                      -> each Guidance, handed over as the fidelity the action works at on it
                           -> FidelityGuidance.render_files format="drawio" paths
                                -> practice_guidance.rendered RenderRequest(fidelity=self)
                                     -> // the request's source, else the format the fidelity works in
                                -> formats[source or fidelity.format].parse content
                                     -> python.parse content
                                          -> CleanEngineeringModel
                                -> formats[format].render model
                                     -> drawio.render model
                                          // keep_positioning / previous stay in drawio/
                 -> act_quickly
                 -> place_rendered

  ----
bdd-behavior (Skill)
  // no model/{format}/ on BDD — companion supplies render
  -> render (Skill)
       -> Render.render guidance format paths
            -> FidelityGuidance.render_files format paths   // a Bdd fidelity
                 -> RenderRequest.companion   // the fidelity's clean_engineering
                      // null → skip (no conversion)
                      -> companion.practice_guidance._render request at the companion fidelity
                           -> // same CleanEngineering loop as above

=========
theme: behaviors
---------
bdd:
a practice
  that has been loaded from its markdown
    it should take each fidelity's default format from that fidelity's Default format
    it should take each fidelity's stage from that fidelity's Stage
    with a format passed at construction
      it should use the passed format
    with no format passed at construction
      it should use the current fidelity's default format
    with a Clean Engineering name on a fidelity
      it should treat that Clean Engineering fidelity as the companion
    with no Clean Engineering name on a fidelity
      it should leave that fidelity without a companion
  that has been asked for guidance
    with a Clean Engineering companion on the current fidelity
      it should include that companion's instructions
    with no Clean Engineering companion on the current fidelity
      it should not include Clean Engineering instructions
  that has been asked to render
    with no format folders
      with no Clean Engineering companion on the current fidelity
        it should skip conversion
    with an object model
      it should render that model into the requested format
    with a tool whose context lives in the code layer
      it should instantiate the object model from that code
      it should render that object model into the requested format

a class model
  that has been generated by the model fidelity
    that has been generated in markdown
      that has been re-rendered in python
        it should be python of that class model
    that has been generated in python
      that has been re-rendered in markdown
        it should be markdown of that class model

a story map
  that has been generated by the story-map fidelity
    that has been generated in markdown
      that has been re-rendered in drawio
        it should be drawio of that story map
    that has been generated in drawio
      that has been re-rendered in markdown
        it should be markdown of that story map

story scenarios
  that have been generated by the scenarios fidelity
    that have been generated in markdown
      that have been re-rendered in python
        it should be python of those scenarios
    that have been generated in python
      that have been re-rendered in markdown
        it should be markdown of those scenarios

aggregate model
  that have been generated by the model fidelity
    that have been generated in markdown
      that have been re-rendered in python
        it should be python of those classes
    that have been generated in python
      that have been re-rendered in markdown
        it should be markdown of those classes

a behavior tree
  that has been generated by the behavior fidelity
    that has been generated in python
      that has been re-rendered in markdown
        it should be markdown of that behavior tree
    that has been generated in markdown
      that has been re-rendered in python
        it should be python of that behavior tree

a render
  that has been invoked with listed practices
    it should return one conversion per practice

