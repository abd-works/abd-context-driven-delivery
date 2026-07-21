path-a : generator produces generator
  Generator : Toolset
    generate
      concepts rules examples templates    <- loaded from module_dir files
      generate_output
      add_generate_header_to_generated
      -> validate

  ----
  domain-toolset.py template
    @generator ClassName
      init

  ----
  produced peer : @generator class
    empty class body
    module_dir has own concepts rules examples templates
    independent manifest

----
path-b : extending with a peer generator
  @generator decorator
    merges annotated class + Generator into new type
    TypeError if class already subclasses Generator

  ----
  extender : merged class
    overridden action
      -> _peer().action         <- peer instantiated at runtime
    @decorator stacked action
      -> super().action         <- reaches Generator base

  ----
  delegation chain example
    AgentBdd
      generate_output -> _bdd().generate
      validate        -> _bdd().validate
      satisfy         -> _bdd().satisfy
    Bdd
      validate        -> _clean_code().validate
      satisfy         -> _clean_code().satisfy

# A: produces the .py file (structural) — output is a peer, not a child
# B: composes behavior at runtime (behavioral) — no class hierarchy
# A and B compose: A writes the shell that B's delegation pattern fills
