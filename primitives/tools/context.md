a class 
    with a class level doc string
    with 2 method annotated with @tool and method level doc strings
        it should provide toolset manifest proprty getter
            that returns a toolset mannifest
            that contain a tool manifest for each tool
            that includes toolset level instructions that match the class doc string
        it should provide a tool manifest property getter on each method
            that matches the tool manifest contained in the toolset manifest
            that contains tool level instructions that match the method doc string
            that contains a machine readable typed signature for the operator, parameters, and return values
            that is invokable using a standardized cli
        with 3 properties annotated with @state and property level doc strings
            its manifest should include a state tool
                that contains a machine readable typed signature to retrieve a collection of the results of the three properties 
        that has been read by an ai agent / chat 
          it should run the tool preproccer
          it should recieve the toolset manifest from the preproccers
          that has invoked the first tool by name
            it should follow the instructions attached to the tool
            it should invoke the tool according to the instructions and the manifest

    ----------
    X toolset
      X   tool  
        X resource

    X agent
      X  toolset

       X instruction
       X     tools
    
       

    generate-tool
        resource.type
    

    specification
        resource.type
        validationResults []
        rules
        abstract validateResults = scan(resource)
          //mechanically check for errors


        abstract validationResults = validateUsingRules (resource)
           """read specification rules and validate wether the resource confirms to the rules,
           with ...from scan call"""
          this.validationResults = scan()
         

        abstract newResource = satisfy (originalResource)
        fixedResource satisfy (resource) 
           validateResults =validate (resource)
           """ examine all validation errors and fix the resource so it  """

       
 generate markdown with fE        
deploy as a skill, 
constrain with actions, rules, instr wtc <-- eg rules       
           
    templated-specification
        template
        abstract validateResults = validate (resource)
           // validate using the template
        satisfy ()
           // does the 

X agentic-tdd
X    """ what is atdd """
X    test-spec:agentic-test-spec


    
agentic-test-spec:
    resource: agentic test
    template
        generate
        validate
        satisfy
