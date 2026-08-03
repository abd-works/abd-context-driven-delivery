stage 2
    
   




Stories   import helper domain
epic folder             
    epic_common_file   < import common objects and helpers
sub epic file          < import objects and helpers
    story classes      < import  unique objects and helpers (rare)
        background
            examples
        scenarios
            examples
            steps      

stories <--

clean_engineering — factory generation PATTERN (framework), not an ExampleLoader type

PATTERN
# {family}.{ext} — production
I{Type}                         // public seam
{Type}                          // production — implements I{Type}

# {type}_example_factory.{ext} — ALWAYS separate
{Type}ExampleFactory
  {example_method}(mode)
    // loads examples[{example_key}] -> I{Type}, I{OtherType}, …
    // Fake | Isolated | Production are modes — not subclasses
// Fake:       mock/stub framework creates I{Type}; feed examples
// Isolated:   new {Type}(...ctor-injected mocks/stubs...)
// Production: new {Type}(...real collaborators...)
// examples[{example_key}] = multi-type bundle (NOT examples[{Type}][…])

EXAMPLE
# cart
ICart / Cart
IProduct / Product
# cart_example_factory
CartExampleFactory
  cart_with_items(mode)
    // examples[cart_with_items] -> ICart, IProduct


    UX (story demo — locked)
        Play: call story given/when/then (same functions that prove the story)
        Interactive: same UI; StoryDemoControl runs whenStep.fn via story_steps (helper.given* only inside When fn)
        Shell: StoryDemoFrame left + ExplorerFrame right (epic → story → scenario → steps)
        After each step: story owns domain; bind via bound_field; emphasize via story_steps
        Play seam: PlayDualRunner (UX story-demo/play-dual-runner) — collect/playNext; node describe/it wrapper
        World/paint: expose(() => ({ …domain variables })); no world bag
        ThenFeedback: peer to PaintReflect — soft-fail Then → message + tint
        UX Story Demo submodule: StoryDemoPage / StoryDemoFrame / ExplorerFrame / StoryDemoControl
          (vanilla Page/Control stay product UX)
        StoryDemoControl.bound_field: display; story_steps: emphasize (Play) + When fn (Interactive)
        Play: explorer Play next only — product controls not invoked

        Primary sketch: context_tools/ux/.context/story-runner-sketch.md
          (themes by user journey; ce → bdd → ux under each)
        Also: ux-context.md · ux-model-sketch.md
        Implemented: UX story-demo (shell + play-dual-runner); sandbox holds engagement HTML wire only


