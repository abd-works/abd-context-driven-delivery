---
name: new-feature
description: New Feature. Takes one new pml-web feature from stakeholder context through definition, a client-side prototype, specification, and LERN implementation, using the CDD skills and Claude Design at each step.
---

# New Feature

Your goal is to take one new feature from stakeholder conversations to a working, tested slice of pml-web. Move through five phases in order: Context, Definition, Prototype, Specification, Implement. Each phase ends with a review in which the user refines and adjusts every artifact the phase touched. Do not start the next phase until the user agrees the current one is done, because errors are cheapest to fix at the fidelity where they first appear.

Keep the slice thin. Work only on the feature the user names, and record anything out of scope as a deferred item rather than building it.

## 1 · Context

Ground the feature in what stakeholders said and what already exists.

- **Open a session for the feature.** Before anything else, tell the user you are creating the session, then run the `space:session:switch-session` skill (MCP `session_switch`) with a kebab-case feature name, `workpath` and `repo_path` set to the repo. The session lives at `.sessions/{feature}/`. Every context file this phase finds or writes goes under `.sessions/{feature}/context/`: transcripts and meeting notes, the stakeholder summary, the existing-artifacts review, and sandbox captures. Move any you already wrote elsewhere into that folder, unless they are already there.
- **Interview stakeholders and transcribe.** Use `tools-granola-context` (or Granola search) to find meetings about this feature, searching with the feature's own name and the words the user used. Save each relevant meeting's notes under `.sessions/{feature}/context/`, plus one `stakeholder-context.md` that summarises what was agreed and what is not yet known. Use `context-setup-convert` for documents the stakeholders share. If no meeting is about this feature, do not widen the search or stretch unrelated meetings to fit. Stop and tell the user you are waiting for the transcription of the initial stakeholder interview. Also ask them to mark up any diagrams or documents (story map, domain model, screens) where they think the change will happen. Continue once the transcript or markups arrive.
- **Review and comment on what exists.** Open the current story map, domain model, and screens. Leave comments on the Miro board where the feature touches them. Use `harness-graph-read-graph` to read the existing model.
- **Plan the walk before you open anything.** Start from the feature's main journey on the story map and pick the area that first decides how the feature works. For a feature that changes what a customer buys, that is onboarding before self-care. For that area, work out the test data needed to reach it: which seeded account or example (the story tests' `examples/` and `signedInAccounts`, the sandbox seed in `scripts/seed-dev-sandbox.ts`), what state it must be in, and whether reaching that state means reseeding or changing sandbox data. Then tell the user the area, the question you are answering there, the screens in order, and the test data you will use, and wait for their feedback before you start.
- **Walk the existing screens in the sandbox.** Tell the user you are opening the sandbox before you do it, and open it in a browser the user can watch, such as the built-in browser pane. Navigate the app in that browser. Before each screen, say which screen you are going to and why. After each screen, say what you found there. Then tell the user you are capturing, and use `context-setup-scout-app` or `context-setup-capture-from-live-app` to capture the screens the feature changes. Finish by listing the screens you visited and where the captures were written.
- Partition and index the material with `actions-partition` and `context-setup-embed`, so every later phase works from verbatim source.

## 2 · Definition

Take stories and domain through both discovery and specification in this one phase, then take UX to specification level, the mockup, in Claude Design.

- **Stories.** Use `actions-sketch` with `practices-stories-stories-story-map` and `practices-stories-stories-scenarios`. Carry the story map through to specification-level scenarios.
- **Domain.** Use `actions-sketch` with `practices-ddd-ddd-bounded-context` and `practices-ddd-ddd-model` to produce the bounded context and the domain model.
- **UX in Claude Design.** Build the mockup as a Claude Design canvas (the Design artifact type), guided by `practices-ux-ux-ia` and `practices-ux-ux-mockup`. Do it inside the sketch when you can: once the stories settle, build the canvas and link it from the sketch's UX section. Otherwise leave UX out of the sketch and build the canvas right after it. Tell the user which way you went.
- **Option: iterate with Miro.** For stories and the domain, the user may choose `actions-iterate` on the Miro board instead of a single sketch. Ask which they prefer.
- **Sketch to spec.** Lift the sketch to specification fidelity with the CDD `transform_sketch` tool, then `actions-generate`.
- **Review.** Run `actions-validate` and `actions-satisfy` on every artifact. Use `actions-grill-context-grill` for open questions. The user refines and adjusts.

## 3 · Prototype

Build a thin slice that behaves: the business logic layer and the client-side layer only.

- **Business logic layer.** Write the domain code the screens call, using `practices-ddd-ddd-tactics` and `practices-clean-engineering-clean-engineering-code`.
- **Client-side layer.** Build the domain client and the views that paint it, following `patterns-lern-domain-driven` and `practices-ux-ux-front-end-code`.
- **Stubbed server.** The server holds a hard-coded map from each route to the next page. It has no persistence and no real business logic.
- **Review.** Run `actions-validate` and `actions-satisfy`. The user refines and adjusts all artifacts. When the prototype is agreed, bring every artifact up to the spec level.

## 4 · Specification

Lock the slice into executable specs before the real stack.

- **Spec tests.** Write the scenarios as tests with `practices-stories-stories-acceptance-tests` and `practices-bdd-bdd-behavior`.
- **Domain code for the client.** Complete the client-side domain code so the spec tests pass, using `practices-ddd-ddd-tactics` and `practices-clean-engineering-clean-engineering-code`.
- **Domain model diagrams.** Complete the tactical domain model with `practices-clean-engineering-clean-engineering-model`, and draw it with `actions-render` to drawio.
- **Clickable mockup.** Wire the stories into a clickable mockup like the UX mockup, but running on the prototype. Use `practices-ux-ux-mockup` and Claude Design.
- **Review.** The user refines and adjusts the specs, code, and diagrams.

## 5 · Implement

Build the feature on the LERN stack and prove it end to end.

- **Acceptance tests.** Use `practices-stories-stories-acceptance-tests`. Hand larger slices to the `implementation` agent.
- **Domain tactics.** Carry aggregates and invariants into production code with `practices-ddd-ddd-tactics`.
- **LERN architecture.** Inject lowdb, Express, React, and Node behind the domain API, following `patterns-lern-domain-driven`.
- **End-to-end tests.** Run the existing Playwright suite and add new specs for the feature, using `practices-bdd-bdd-realization`. Where the feature replaces a pml-my screen, check parity with `stories-legacy-compare`.
- **Review.** All acceptance and end-to-end tests pass, and the user confirms the feature.

## Handoff

Run `space-handoff-handoff-session` when the feature is done or the session ends. Name the phase reached, the artifacts and files changed in each phase, decisions and their reasons, test commands and results, deferred items, and the next exact step. Feed what was learned back into context, so the next feature starts from it.
