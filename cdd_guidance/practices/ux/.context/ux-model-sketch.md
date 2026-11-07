# UX canonical model + format conversion — language sketch

// Flow: drawio (ia) → html (mockup/spec). MD carries scope and context notes only — not the primary UX surface.
// story_references / object_references: paths to Stories JS / object-model JS (CE).
// Layout (colocated):
//   .context/information-architecture.drawio + ux-sketch.md + ux-context.md
//   epic root: ux-map.json + <folder>.html ; mockup HTML may also sit in sub-epic folders
// Transition / ContentType / NavComponent are UxComponent subtypes.
// Collections Transitions / ContentTypes / NavComponents own append / remove / find.
// Classes and signatures: practices/ux/model/.context/ux-model.md

UxMap
  scope
  append_screen screen
  find_screen name
  story_references
    // property — paths to Stories JS artifacts (references only)
  object_references
    // property — paths to object-model JS artifacts (CE)
  transitions Transitions
  content_types ContentTypes
  nav_components NavComponents
  screens
       Screen
         name
         slug
         layout
         apply_layout layout_id
              // records the layout name; the caller appends the regions
         append_region region
         show_story story
         show_scenario scenario
              // the Scenario, or its key Story › Scenario
         show_step step
              // the Step, or its key Story › Scenario › Step — each becomes a StoryLink and a shownOn edge on the graph
         shows
              // the Stories nodes on the screen's graph it shows
         attach_domain_term term
         domain_concepts
              // vocabulary labels for rules — not object-model JS
              Region
                name
                area
                append_control control
                     Control
                       name
                       control_type
                       label
                       bound_field
                       states
                       append_interaction interaction
                            Interaction
                              trigger   // click | hover | drag | change | …
                              effect
                              destination
                                   // the Screen itself
                       // plain control — no story_steps
  context UxContext
         notes
         invariants

  ----
 StoryDemoControl : Control           // UX Story Demo submodule (not every page)
  bound_field
    // expose() path to show on bind — display only; does not own domain
  story_steps
    // control ↔ GWT kind+label
    // Play: emphasize only (product control not invoked)
    // Interactive: which When step.fn Interaction runs
    // (not helper.given* from the control — that stays in the When fn)
    // HTML render: data-story-steps
  set_input
  item_story_steps
  item_value
  item_label
  // JS (story-demo/control.js): show value, emphasize / clearEmphasis, tint
  ----
 StoryDemoPage                        // UX Story Demo shell document (story-demo/story-demo-page.js)
  storyDemoFrame StoryDemoFrame       // LEFT — product UI
  explorerFrame ExplorerFrame         // RIGHT — story tree / Play next
  mode                                // Play | Interactive
  ----
 StoryDemoFrame                       // LEFT pane
  controls[]                          // StoryDemoControl[]
  bind snapshot
  emphasize step
  tintFailed result
  ----
 ExplorerFrame                        // RIGHT pane
  storyTree
  playNextControl
  ----
 UxComponent
      name
  ----
 Transition : UxComponent
      from_screen
      to_screen
      trigger
      nav_type
  ----
 ContentType : UxComponent
      hierarchy
      key_actions
  ----
 NavComponent : UxComponent
      ux_type
      destinations
  ----
 UxComponentCollection
      append component
      remove name
      find name
  ----
 Transitions : UxComponentCollection
  ----
 ContentTypes : UxComponentCollection
  ----
 NavComponents : UxComponentCollection
  ----
 ReferencePaths
      // ordered, de-duplicated path strings
      add path
      replace paths
  ----
 // No LayoutTemplate catalog - Screen.apply_layout(id) just records the
 // layout name; the AI reads the matching pair under
 // specifications/generic/ (or a branded sibling under specifications/)
 // for that layout's areas and appends the real Regions itself
  ----
 UxMap formats                        // each a UxMap subclass
      parse content
       -> UxMap
      render ux_map
      from_workspace root
       -> parse the format's file in root
  ----
 DrawioUxMap : UxMap
      // render via drawio-ux CLI → Detailed IA + Site Map
  ----
 HtmlUxMap : UxMap
      // mockup review shell; parse reads back the embedded JSON map
  ----
 MarkdownUxMap : UxMap
  ----
 JsonUxMap : UxMap
  ----
 ClaudeDesignUxMap : UxMap
      // screen boards on the canvas; never parsed back
  ----
 Ux
      fidelity
      format
      render format content source
       -> source format.parse
       -> target format.render
      ensure_javascript practice source_format content
