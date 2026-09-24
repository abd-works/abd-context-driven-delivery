# Modules

*Context-Driven Delivery* is how an agent installs practices, opens a work session, and runs generate, document, and scan from the markdown that sits beside the code. Public classes and dependencies below are the CodeQL first-class module prefixes and `moduleDependsOn` edges — not a curated seam.

## actions
### Public Seam
#### Document

#### Generate

#### Render

#### Satisfy

#### Validate

### Dependencies
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## builders
### Public Seam

*(no public classes in the graph)*

### Dependencies
 - *(none in the graph)*
---

### Constraint

*(none in the graph)*

## harness
### Public Seam
#### AppliesTo

#### FidelityGuidance

#### Guidance

#### GuidanceAction

#### GuidanceCollection

#### Markdown

#### OtherTool

#### PracticeGuidance

#### Render

#### Rule

#### RulesCollection

#### SampleAgenticOps

#### SampleGuidance

#### SampleHookOps

#### SampleMcpGuidance

#### SampleMcpOps

#### SampleMcpPractice

#### SamplePracticeGuidance

#### SamplePracticeWithFidelities

#### SampleTool

#### Session

#### SplitPracticeGuidance

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## installation
### Public Seam
#### Agent

#### AgentGuidance

#### Command

#### Destination

#### FileInstallation

#### Installation

#### Installer

#### Rules

#### Skill

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices
### Public Seam

*(no public classes in the graph)*

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## tools
### Public Seam

*(no public classes — each tool owns its own module-context)*

### Dependencies
 - *(none — children declare their own)*
---

### Constraint

This folder is not a first-class module. Callers import `tools.workspace`, `tools.git`, …

## actions.grill_context
### Public Seam
#### GrillContext

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.iterate` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## actions.improvement
### Public Seam
#### Improvement

### Dependencies
 - `actions.sketch` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## actions.iterate
### Public Seam
#### Iterate

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.grill_context` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## actions.partition
### Public Seam
#### Partition

#### PartitionIndex

#### Segment

#### SegmentCompletenessConfig

#### SegmentEntry

### Dependencies
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## actions.sketch
### Public Seam
#### Sketch

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.grill_context` — moduleDependsOn
 - `actions.iterate` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## builders.create_agent_toolset
### Public Seam
#### CreateAgentToolset

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## builders.create_context_tool
### Public Seam
#### CreateContextTool

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## harness.agent_tools
### Public Seam
#### AgentInstructions

#### AgentInstructionsMark

#### AgentOperation

#### AgentTool

#### AgentToolDestination

#### AgentToolMark

#### AgentToolSet

#### AgentToolSetMark

#### AgentToolSetOrigin

#### AgentToolSetTools

#### AgentToolValidationError

#### Collect

#### ExpansionMode

#### ExpansionResult

#### InstallDestination

#### ToolSetCollection

#### ToolSetCollectionMark

#### ToolsetManifest

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## harness.hooks
### Public Seam
#### CursorEvent

#### HandlerCatalog

#### Hook

#### HookDaemon

#### HookHandler

#### HookIllegitimateHandler

#### HookInstallation

#### HookPayload

#### HookResult

#### HookServer

#### HookStandupFailed

#### Hooks

#### SessionLogs

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## harness.knowledge_graph
### Public Seam
#### CodeQL

#### CodeQLBackground

#### CodeQLCall

#### CodeQLClass

#### CodeQLExampleExport

#### CodeQLOperation

#### CodeQLPopulate

#### CodeQLPracticeGraphExport

#### CodeQLProperty

#### CodeQLRunError

#### CodeQLScenario

#### CodeQLStep

#### CodeQLStory

#### CodeQLStoryCall

#### CodeQLStoryObservation

#### DotMarkup

#### Failures

#### FidelityGuidance

#### Filter

#### GraphAggregate

#### GraphBackground

#### GraphBoundedContext

#### GraphClass

#### GraphCleanEngineeringModel

#### GraphContext

#### GraphDescription

#### GraphDomainEvent

#### GraphDomainService

#### GraphEntity

#### GraphEntityRoot

#### GraphEpic

#### GraphExample

#### GraphLoader

#### GraphModule

#### GraphObservation

#### GraphOperation

#### GraphParameter

#### GraphProperty

#### GraphQueryRun

#### GraphRepository

#### GraphRule

#### GraphRulesCollection

#### GraphScenario

#### GraphStep

#### GraphStory

#### GraphStoryMap

#### GraphSubEpic

#### GraphValueObject

#### HookServer

#### Kind

#### KnowledgeGraph

#### McpServer

#### Node

#### NodeRelations

#### NodeRules

#### NodeView

#### NodeWalk

#### PracticeGraph

#### PracticeGuidance

#### PromptEcho

#### QueryServerDown

#### Relationship

#### Rows

#### Rule

#### RuleRegistry

#### RuleSlugs

#### RuleTiming

#### RuleViolation

#### RulesCollection

#### Session

#### StorySourceQuery

#### Validate

#### VocabularyHelper

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## harness.markdown
### Public Seam
#### AssetLocation

#### AssetLocator

#### HTML

#### Markdown

#### MarkdownCollection

#### MarkdownFile

#### MarkdownSlot

#### MarkdownText

#### YamlBinder

### Dependencies
 - `actions.partition` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## harness.mcp
### Public Seam
#### CodeQLQueryServer

#### CursorMcpJson

#### HostDiscovery

#### HostPid

#### Mcp

#### McpHost

#### McpIllegitimateTool

#### McpInstallation

#### McpOperationDefinition

#### McpPrompt

#### McpServer

#### McpStandupFailed

#### McpTool

#### QueryServerClient

#### StartHost

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.agent_bdd
### Public Seam
#### AgentBdd

#### AgentBddConf

#### AgentBlockLocal

#### AgentHarnessError

#### AgentJudgeError

#### AgentResult

#### AgentSession

#### AgentSpecManifest

#### AgentSpecRunbook

#### ChatInboxPending

#### HarnessLog

#### JudgeResult

#### RunResponse

#### ToolsRunYaml

#### ToolsetInvoke

#### YamlFence

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.bdd
### Public Seam
#### Bdd

#### Context

#### Description

#### Observation

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.clean_engineering
### Public Seam
#### ArgNamingScanner

#### AskCrossAggregateSyncScanner

#### CallInfo

#### CasingTransformScanner

#### ClassInfo

#### CleanEngineering

#### CrossLayerNamingScanner

#### DependencyDeclarationsScanner

#### DomainStructureScanner

#### EntityBehaviorScanner

#### ImportInfo

#### InterfaceImplementationScanner

#### InterfaceInfo

#### LERNScanner

#### LayerPurityScanner

#### LernDomainDriven

#### MERNScanner

#### MernDomainDriven

#### MethodInfo

#### MutationResponseScanner

#### OneJsonStorePerAggregateScanner

#### PackageNamesScanner

#### PropertyInfo

#### RepositoryOwnsAggregateLifecycleScanner

#### RouteDelegationScanner

#### Scan

#### ScanReport

#### Scanner

#### ScannerCollection

#### ScannerReport

#### ShareDomainLogicScanner

#### TestIsolationScanner

#### TestScriptsScanner

#### TestStructureScanner

#### TypeSafetyScanner

#### TypeScriptScanner

#### UbiquitousLanguageScanner

#### ViewNamingScanner

#### Violation

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.grill_context` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.clean_engineering.model
### Public Seam
#### CFamilyParse

#### Change

#### ChangeKind

#### ChildCollectionPair

#### CleanEngineeringModel

#### ContainmentForest

#### DiagramClass

#### DiagramModule

#### DiagramNode

#### File

#### Geometry

#### GraphMemberRows

#### ImportedClass

#### JavaCleanEngineeringModel

#### JavaOoadClass

#### JavaScriptCleanEngineeringModel

#### JavaScriptModule

#### JavaScriptOoadClass

#### JavaScriptOperation

#### JavaScriptProperty

#### JsonCleanEngineeringModel

#### JsonModule

#### JsonOoadClass

#### JsonOperation

#### JsonParseError

#### JsonProperty

#### JsonRelationship

#### MarkdownCleanEngineeringModel

#### MarkdownModule

#### MarkdownOoadClass

#### MiroClass

#### MiroCleanEngineeringModel

#### MiroImportedClass

#### MiroModule

#### Module

#### ModuleContext

#### ModuleContextFiles

#### OoadClass

#### OoadNode

#### Operation

#### OperationField

#### Page

#### Parameter

#### ParsedPython

#### Property

#### PropertyField

#### PythonCleanEngineeringModel

#### PythonModule

#### PythonOoadClass

#### Relationship

#### Responsibilities

#### SourceSpan

#### TranslationError

#### TypeScriptCleanEngineeringModel

#### TypeScriptModule

#### TypeScriptOoadClass

#### TypeScriptOperation

#### TypeScriptProperty

#### UpdateReport

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.clean_engineering.model.drawio
### Public Seam
#### BaseAboveDerivedScanner

#### ClassTitleNoMarkdownBoldScanner

#### DistinctAnchorPointsScanner

#### DrawIOClass

#### DrawIOCleanEngineeringModel

#### DrawIOModule

#### Drawio

#### DrawioScanner

#### DrawioViolation

#### EdgesApproachPerpendicularScanner

#### EdgesDoNotCrossClassesScanner

#### EdgesDoNotCrossOtherEdgesScanner

#### EdgesDoNotOverlapEdgesScanner

#### ImportedClass

#### LeafNodesNotInHorizontalRowScanner

#### Page

#### PreferShortRoutesScanner

#### StereotypeAboveClassNameScanner

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.ddd
### Public Seam
#### Aggregate

#### AggregateEntry

#### BoundedContext

#### BoundedContextEntry

#### Cart

#### Ddd

#### DomainEvent

#### DomainService

#### Entity

#### EntityRoot

#### Plan

#### Repository

#### SelectSim

#### ValueObject

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.kanban
### Public Seam

*(no public classes in the graph)*

### Dependencies
 - *(none in the graph)*
---

### Constraint

*(none in the graph)*

## practices.stories
### Public Seam
#### ArchitectureContext

#### Background

#### Cart

#### Change

#### ChangeKind

#### ChildCollectionPair

#### Clause

#### CodeStoryMap

#### CodeStoryMapError

#### DiagramStoryMap

#### DrawIOEpic

#### DrawIOIncrement

#### DrawIOParseError

#### DrawIOScenario

#### DrawIOStory

#### DrawIOStoryMap

#### DrawIOSubEpic

#### Epic

#### Example

#### ExampleFactories

#### HelperMethod

#### Increment

#### Interaction

#### JavaEpic

#### JavaScenario

#### JavaScriptEpic

#### JavaScriptExampleFactories

#### JavaScriptScenario

#### JavaScriptStory

#### JavaScriptStoryMap

#### JavaScriptSubEpic

#### JavaScriptTree

#### JavaStory

#### JavaStoryMap

#### JavaSubEpic

#### JavaTree

#### JsonEpic

#### JsonIncrement

#### JsonParseError

#### JsonScenario

#### JsonStory

#### JsonStoryMap

#### JsonSubEpic

#### Language

#### MarkdownEpic

#### MarkdownIncrement

#### MarkdownParseError

#### MarkdownScenario

#### MarkdownStory

#### MarkdownStoryMap

#### MarkdownSubEpic

#### MiroApiClient

#### MiroApiError

#### MiroAuthError

#### MiroEpic

#### MiroIncrement

#### MiroParseError

#### MiroScenario

#### MiroStory

#### MiroStoryMap

#### MiroSubEpic

#### MiroUploader

#### NodeSnapshot

#### Phase

#### PlacementError

#### PythonEpic

#### PythonExampleFactories

#### PythonScenario

#### PythonStory

#### PythonStoryMap

#### PythonSubEpic

#### PythonTree

#### Scenario

#### SourceLocation

#### Step

#### StepBody

#### Stories

#### Story

#### StoryContext

#### StoryExampleCollector

#### StoryMap

#### StoryNames

#### StoryNode

#### StoryNodeTransformer

#### StoryType

#### SubEpic

#### Test

#### TestCase

#### TestSuite

#### Tier

#### TranslationError

#### TypeScriptEpic

#### TypeScriptScenario

#### TypeScriptStory

#### TypeScriptStoryMap

#### TypeScriptSubEpic

#### TypeScriptTree

#### UpdateReport

#### Vertex

#### Workspace

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.ux
### Public Seam
#### Ux

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.ux.model
### Public Seam
#### Change

#### ChangeKind

#### ChildCollectionPair

#### ContentType

#### ContentTypes

#### Control

#### Interaction

#### NavComponent

#### NavComponents

#### ReferencePaths

#### Region

#### Screen

#### StoryDemoControl

#### Transition

#### Transitions

#### TranslationError

#### UpdateReport

#### UxComponent

#### UxComponentCollection

#### UxContext

#### UxMap

#### UxNode

#### Workspace

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.ux.model.drawio
### Public Seam
#### DrawioUxMap

### Dependencies
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.ux.model.html
### Public Seam
#### HtmlUxMap

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.ux.model.json
### Public Seam
#### JsonUxMap

### Dependencies
 - `harness.knowledge_graph` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.ux.model.markdown
### Public Seam
#### MarkdownUxMap

### Dependencies
 - `harness.knowledge_graph` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.ux.scripts
### Public Seam

*(no public classes in the graph)*

### Dependencies
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## practices.ux.story-demo
### Public Seam

*(no public classes in the graph)*

### Dependencies
 - *(none in the graph)*
---

### Constraint

*(none in the graph)*

## practices.ux.story-demo.play-dual-runner
### Public Seam

*(no public classes in the graph)*

### Dependencies
 - *(none in the graph)*
---

### Constraint

*(none in the graph)*

## tools.workspace
### Public Seam
#### WorkSession
#### WorkSessionGuidance
#### WorkSessionRulesCollection
#### WorkSessionRule
#### Turn
#### TurnCommit
#### Workspace
#### SessionLog
#### ISessionLog
#### SessionModel
#### SessionPaths
#### PathOverride
#### ToolCall
#### Example
#### Examples
#### Mistake
#### Correction
#### Repair
#### Repairs
### Dependencies
 - `tools.git` — uses
---

### Constraint

*(none named in this file yet)*

## tools.prompt_log
### Public Seam
#### PromptLog
### Dependencies
 - `harness.hooks` — uses
 - `harness.agent_tools` — uses
---

### Constraint

`@Hooks(disabled=True)` on *PromptLog* skips every audit handler.

## tools.context_setup
### Public Seam
#### ContextSetup
#### ContextIndex
#### RankedChunk
#### EmbedResult
#### SearchResult
#### EmbeddingProvider
#### OpenAIEmbeddingProvider
#### StructureNote
#### ConversionResult
#### ScreenResult
#### SmokeTestResult
#### PageCapture
#### ScoutResult
#### CaptureResult
### Dependencies
 - `actions.partition` — uses
 - `practices.clean_engineering` — uses
 - `practices.ddd` — uses
 - `practices.stories` — uses
 - `practices.ux` — uses
---

### Constraint

*(none named in this file yet)*

## tools.catalog_generator
### Public Seam
#### ActionResolution

#### Brand

#### Catalog

#### CatalogAction

#### CatalogContextTool

#### CatalogFidelity

#### CatalogFidelityGuidance

#### CatalogPage

#### CatalogTool

#### CatalogUtility

#### GitCitation

#### HeadingSection

#### IllustratedExampleRow

#### RegistryEntry

#### SkillSlashName

#### TemplateFrontmatter

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `practices.ux.model.drawio` — moduleDependsOn
 - `practices.ux.model.html` — moduleDependsOn
 - `practices.ux.model.json` — moduleDependsOn
 - `practices.ux.model.markdown` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## tools.diagnose
### Public Seam
#### Diagnose

### Dependencies
 - `harness.hooks` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## tools.echo
### Public Seam
#### Echo

### Dependencies
 - `harness.agent_tools` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## tools.git
### Public Seam
#### Branch

#### CliAgentBinding

#### Commit

#### DirtyBranchSwitchError

#### GhConnectError

#### Git

#### GitConnectError

#### Project

#### ProjectItem

#### Repo

#### Ticket

#### TicketNotFoundError

#### TicketState

#### Worktree

### Dependencies
 - `actions` — moduleDependsOn
 - `actions.partition` — moduleDependsOn
 - `actions.sketch` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `builders.create_context_tool` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.markdown` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.clean_engineering.model` — moduleDependsOn
 - `practices.clean_engineering.model.drawio` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## tools.handoff
### Public Seam
#### Handoff

### Dependencies
 - `harness.knowledge_graph` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.git` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## tools.plan
### Public Seam
#### HILCheck

#### JudgeCheckpoint

#### Plan

#### PlanCommands

#### PlanExecution

#### PlanSeed

#### PlanTurns

#### ProgressView

#### SmallWorkRunner

#### SmallWorkState

#### ThemedIssue

#### TurnAttachments

#### TurnTemplate

### Dependencies
 - `actions.partition` — moduleDependsOn
 - `harness` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.prompt_echo` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## tools.prompt_echo
### Public Seam
#### Echo

#### FidelityGuidance

#### Generate

#### GuidanceAction

#### PracticeGuidance

#### PromptEcho

#### Sketch

### Dependencies
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `installation` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.workflow` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## tools.record_decisions
### Public Seam
#### RecordDecisions

### Dependencies
 - `harness.agent_tools` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
---

### Constraint

*(none in the graph)*

## tools.workflow
### Public Seam
#### WorkTicket

#### Workflow

#### WorkflowConfig

### Dependencies
 - `actions.partition` — moduleDependsOn
 - `builders.create_agent_toolset` — moduleDependsOn
 - `harness.agent_tools` — moduleDependsOn
 - `harness.hooks` — moduleDependsOn
 - `harness.knowledge_graph` — moduleDependsOn
 - `harness.mcp` — moduleDependsOn
 - `practices` — moduleDependsOn
 - `practices.agent_bdd` — moduleDependsOn
 - `practices.clean_engineering` — moduleDependsOn
 - `practices.ddd` — moduleDependsOn
 - `practices.stories` — moduleDependsOn
 - `practices.ux.model` — moduleDependsOn
 - `tools` — moduleDependsOn
 - `tools.catalog_generator` — moduleDependsOn
 - `tools.diagnose` — moduleDependsOn
 - `tools.git` — moduleDependsOn
 - `tools.handoff` — moduleDependsOn
 - `tools.plan` — moduleDependsOn
---

### Constraint

*(none in the graph)*
