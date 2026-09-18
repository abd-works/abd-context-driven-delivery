AgentToolCatalog
    ToolSets
        Toolset  <- existing
            Instantiate
            Reference
            Operations
            Instructions
            Tools
                AgentTool
                    Signature
                    Reference
                    Instantiate
                    CurrentInstallation <--new
        NestedTools
    Tools [name]  <--nested path eg package.class.operation / property
    Operations [name]
    Instructions [name]

