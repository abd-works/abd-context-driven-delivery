generate

  

car


generator : toolset
    instructions -> "generate new or update knowledge artifact"
    contexts
    examples
    rules
    template
       
    @resource
    generated-knowledge

    @action
    generate() 
        "generate using template... guided by rules and examples" 
        r =self.rules()
        e = self.examples()
        template = self.template()
        self.generate-output()
        "once generated please take the role of a ai judge and validate using"
        validations = self.validate(knowledge)
        "and fix...."


Story


  @context_tool
  story-map
    " a story map is a ...."
    @generate-output
    generate(epic[], format=python, existingStoryMap)
        "create the story-map .... build it on an epic by epic basis, going as deep as you need to so that u only build 10-20 stories worth of epics ar a time, calling "
     
        self.addEpic(epic)
        " as manty rimes as required to save the map, for example an initial call may insert the higer level epic / subepic structure and later calls may insert lower level epics to those epics using one of"
        epic.addSubEpic(lowerLevelEpic)
        lowerLevelEpic.addStory(story)
        "if existingStoryMap exists then we need to determine the updates and call "
        epic.update(lowerLevelEpic)
        lowerLevelEpic.update(story)
        
        lowerLevelEpic.delete(story)
        story["Driving Car"].name = "Drive Car"
        
        
        , "at lowest possible point in the map"
        "once story map model is correct, save the model using the correct format"
        self.render(format)


    "add a story node to the story map at the given path"
    add(path,storyNode)


    "delete node from the story map and all its children"
    delete(storyNode)

    "replace the story node and replace all attached children; ensure ordering, removals, aqdditions are resprected
    update(path,story Node)


behavior-driven-development
    



------------
clean-code
     
  



    ======



    behaviors[]
        description
        subject-under-test
        before hooks
        contexts[]
            descripton
            specs[]
                code
            contexts[]
                   spec



block
    description
    children

behavior 
    subject
    hooks
    contexts

context
    hooks
    contexts
    specs

Spec
    copde
    expectations

expectation
   code

 hook    
    when: before | tear-down
    scope: each | all



   


stories
   story-map
      generate 
         subject 
        format

   story map  --
    description <--
  epics
    epic
      stories
  --------------------------------       
        story
            background
            examples
            scenarios
                test case
                  
                examples
            step
                
      

  generate