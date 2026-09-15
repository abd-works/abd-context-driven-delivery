---
name: sketch
description: "Sketch then generate - grill + sketch cadence, then the host generate body."
disable-model-invocation: true
---

# sketch

Run this action for any provided context tools, or on the context in general.

Sketch a solution interactively before generating the formal artifact.

Sketch then generate - grill + sketch cadence, then the host generate body.

Sketch interactively - rough artifact through an explicit grill_with_context call. MUST persist via save_sketch on the first interim draft and overwrite on every refinement. Never leave the sketch only in chat. destination defaults to session.path (durable {path}/.context/) — not session.folder. Module sketches: {session.path}/{module}. Question shape (frame + options) comes from grill_with_context - do not restate bare options here. Hard rule: call save_sketch as soon as the first interim draft exists; overwrite on every regeneration; call review_sketch after every save_sketch and do not ask the next grill question until the person confirms the sketch is correct. Never defer persistence or review to the end of the grill. Mistakes named in review (bad assumptions, poor performance, poor hygiene, or anything else) must be carried forward into the next sketch — correct the model; do not regenerate as if those mistakes never happened. Grill validates what the sketch claimed — sketch and grill must not run disconnected.

Step 0 - Grill the sketch plan (concept-grounded, thinking-first questions via grill_with_context). Batch very similar questions into one AskQuestion when they share a frame (e.g. port-as-is vs change for several peers) so the loop does not run forever.

Step 1 - Resolve destination: session.path (or session.docs_dir). Module -> {session.path}/{module}. If no session sprint exists yet, confirm path with the user, suggest a kebab slug, open, then use session.path. Do not invent {path}/.context/{session-name}/ or write the sketch into sessions/{name}/.

Step 2 - locate the sketch template via find_template(agent_dir=agent_dir). agent_dir is the concrete host toolset module directory (manifest chain agent_dir / module_dir of the invoked Context). If the caller supplied a template directly in context, use that instead.

Step 3 - draft a rough sketch inspired by the template. Show it in chat, then IMMEDIATELY call save_sketch(destination, slug, content), then IMMEDIATELY call review_sketch. A sketch that exists only in chat is a defect - the file under the destination docs dir is the working record. Asking another grill question before review_sketch confirms correct is a defect.

Step 4 - After every 2-3 grill answers (or one batched multi-choice), regenerate the sketch showing exactly what changed AND incorporating every mistake named in prior review_sketch rounds, show it in chat, IMMEDIATELY call save_sketch again (same path), then IMMEDIATELY call review_sketch again. Regenerating as if named mistakes never happened is a defect. Use placeholders for unresolved branches. Do not write formal generate artifacts during the sketch loop - that is iterate/generate territory.

Step 5 - Repeat until the sketch is stable, the user is satisfied, or the user switches to iterate/generate. Every new grill question still follows grill's Step 3a-3b and must wait for review_sketch confirmed-correct; this stage owns sketch persist/show/review cadence and uses grilling to validate the sketch. Carry forward all named mistakes into each next sketch.

With a straight prompt passed, run this action on the context in general. If you took a context tool from the context and not a straight prompt, confirm the use of the context. AskQuestion constrained to the context tools: agent-bdd | bdd | car | cdd | clean-engineering | create-context-tool | ddd | harness | stories | ux | use existing context only.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities.
Then run:
Use MCP tool: `sketch.sketch(tools: 'list') -> 'str'`
