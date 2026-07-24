# UX canonical model + channel conversion — language sketch

// Flow: drawio (ia) → html (mockup/spec). MD optional context only — not primary UX surface.
// story_references / object_references: paths to Stories JS / object-model JS (CE).
// Layout (colocated):
//   .context/information-architecture.drawio + ux-sketch.md + ux-context.md
//   epic root: ux-map.json + <user-goal>.html ; mockup HTML may also sit in sub-epic folders
// Transition / ContentType / NavComponent are UxComponent subtypes.
// Collections Transitions / ContentTypes / NavComponents own append / remove / find.

UxMap
  scope
  append_screen screen
  find_screen name
  story_references
    // property — paths to Stories JS artifacts (references only)
  object_references
    // property — paths to object-model JS artifacts (CE); domain not built yet
  transitions Transitions
  content_types ContentTypes
  nav_components NavComponents
  screens
       Screen
         name
         slug
         layout
         apply_layout layout_id
              // thin catalog → sets layout + seeds empty regions from slots
         append_region region
         bind_domain_concept concept_name
              // vocabulary label for scanners — not object-model JS
              Region
                name
                slot
                append_control control
                     Control
                       name
                       control_type
                       label
                       append_state state_name
                       append_interaction interaction
                            Interaction
                              trigger   // click | hover | drag | change | …
                              effect
                              destination_screen
                       // vanilla — no bound_field / story_steps / emphasize / tint
  context UxContext
         notes
         invariants

  ----
 StoryDemoControl : Control           // UX Story Demo submodule (not every page)
  bound_field
    // expose() path to show on bind — display only; does not own domain
  story_steps
    // bind control ↔ GWT kind+label
    // Play: emphasize only (product control not invoked)
    // Interactive: which When step.fn Interaction runs
    // (not helper.given* from the control — that stays in the When fn)
    // HTML render: data-story-steps
  show value
  emphasize / clearEmphasis
  tint
  ----
 StoryDemoPage                        // UX Story Demo shell document
  storyDemoFrame StoryDemoFrame       // LEFT — product UI
  explorerFrame ExplorerFrame         // RIGHT — story tree / Play next
  mode                                // Play | Interactive
  ----
 StoryDemoFrame                       // LEFT pane (was MockupFrame)
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
 LayoutTemplate
      id
      slots
      // thin catalog in layouts.py — not ASCII/drawio paste library
  ----
 UxChannel
      parse content
       -> UxMap
      render ux_map
  ----
 DrawioUxChannel : UxChannel
      // render via drawio-ux CLI → Detailed IA + Site Map
  ----
 HtmlUxChannel : UxChannel
  ----
 MarkdownUxChannel : UxChannel
  ----
 JsonUxChannel : UxChannel
  ----
 Ux
      fidelity
      format
      generate
      validate
      transform source_format target_format content
       -> source_channel.parse
       -> target_channel.render
  ----
 UxWorkspace
      load root
       -> DrawioUxChannel.parse
       -> HtmlUxChannel.parse
      ux_map
      story_references
      object_references
