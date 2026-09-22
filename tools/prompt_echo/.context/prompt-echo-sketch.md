fidelity: model
scope: PromptEcho @echo
status: agreed — generate model from this sketch

=========
theme: where the marks go
---------
ce:
GuidanceAction
  begin guidance action
       // @echo here — one mark; every kit runs this
  run guidance operation
       -> begin
  open_workspace
       // not the action echo

Generate : GuidanceAction
  generate
       -> run                    // later @echo on this method still works

Sketch : GuidanceAction
  sketch
       -> begin                  // later @echo on this method still works

  ----
 PracticeGuidance : Guidance
  instructions
       // @echo independent of begin

  ----
 FidelityGuidance : Guidance
  instructions
       // @echo independent of begin

=========
theme: PromptEcho lookup
---------
ce:
Echo : Destination
  apply operation
       // sets _echo on the callable

PromptEcho
  on_pre_tool_use payload
       -> handle payload
            -> show_ide_toast
  handle payload
       // invoked member _echo → toast that member
       // else toolset begin _echo → Action → kit name
