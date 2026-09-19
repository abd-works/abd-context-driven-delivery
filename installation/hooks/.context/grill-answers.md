# Grill Answers

### One action mark covers every kit

Put @echo on GuidanceAction.begin in harness/guidance_actions/guidance_actions.py. Every kit reaches begin: run() always calls begin (generate, document, scan, validate, …); sketch and grill call begin directly. run itself is not an AgentTool. open_workspace is the wrong event.

### Per-method echo still works later

PromptEcho on preToolUse toasts if the invoked callable has _echo. If not, it walks the toolset and toasts as Action when inherited begin has _echo. A later @echo on Generate.generate (or any other method) still fires for that invoke without removing the begin mark.

### Instructions echo is independent

Separately mark PracticeGuidance.instructions and FidelityGuidance.instructions in harness/guidance/guidance.py. Those MCP prompts are not GuidanceAction.begin; practice/fidelity toasts do not require the action mark.

