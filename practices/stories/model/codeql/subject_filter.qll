import javascript

predicate subjectFilterPrefix(string prefix) { prefix = "" }

predicate firstClassModulePrefix(string prefix) {
  prefix = "actions/grill_context" or
  prefix = "actions/improvement" or
  prefix = "actions/iterate" or
  prefix = "actions/partition" or
  prefix = "actions/sketch" or
  prefix = "builders/create_agent_toolset" or
  prefix = "builders/create_context_tool" or
  prefix = "harness/agent_tools" or
  prefix = "harness/hooks" or
  prefix = "harness/knowledge_graph" or
  prefix = "harness/markdown" or
  prefix = "harness/mcp" or
  prefix = "harness/transformers/fixtures/mm3e/ability" or
  prefix = "harness/transformers/fixtures/mm3e/advantage" or
  prefix = "harness/transformers/fixtures/mm3e/character_construction" or
  prefix = "harness/transformers/fixtures/mm3e/checks" or
  prefix = "harness/transformers/fixtures/mm3e/combat" or
  prefix = "harness/transformers/fixtures/mm3e/equipment" or
  prefix = "harness/transformers/fixtures/mm3e/power" or
  prefix = "harness/transformers/fixtures/mm3e/skill" or
  prefix = "installation" or
  prefix = "practices" or
  prefix = "practices/agent_bdd" or
  prefix = "practices/bdd" or
  prefix = "practices/clean_engineering" or
  prefix = "practices/clean_engineering/model" or
  prefix = "practices/clean_engineering/model/drawio" or
  prefix = "practices/ddd" or
  prefix = "practices/kanban" or
  prefix = "practices/stories" or
  prefix = "practices/ux" or
  prefix = "practices/ux/model" or
  prefix = "practices/ux/model/drawio" or
  prefix = "practices/ux/model/html" or
  prefix = "practices/ux/model/json" or
  prefix = "practices/ux/model/markdown" or
  prefix = "practices/ux/scripts" or
  prefix = "practices/ux/story-demo/play-dual-runner" or
  prefix = "tools/catalog_generator" or
  prefix = "tools/context_setup" or
  prefix = "tools/diagnose" or
  prefix = "tools/echo" or
  prefix = "tools/git" or
  prefix = "tools/handoff" or
  prefix = "tools/plan" or
  prefix = "tools/prompt_echo" or
  prefix = "tools/prompt_log" or
  prefix = "tools/record_decisions" or
  prefix = "tools/workflow" or
  prefix = "tools/workspace" or
  prefix = "harness/guidance" or
  prefix = "harness/guidance_actions" or
  prefix = "harness/session" or
  prefix = "harness/transformers" or
  prefix = "actions/document" or
  prefix = "actions/generate" or
  prefix = "actions/render" or
  prefix = "actions/satisfy" or
  prefix = "actions/validate"
}

predicate inSubject(AstNode n) {
  inSubjectPath(n.getLocation().getFile().getRelativePath().replaceAll("\\", "/"))
}

bindingset[path]
predicate inSubjectPath(string path) {
  any()
}
