# CDD — Procedural Guidance (discovery fidelity)

## How to run discovery

Discovery shapes the whole solution or a large subsection. The scope is wide, the detail is thin:

1. **Identify the scope** — entire solution, or a major product area. Discovery doesn't zoom into a single sub-epic.
2. **Choose active lenses** — which perspectives matter for this scope? Usually all of them at discovery, but confirm with the user.
3. **Order themes by journey** — when the theme is the customer journey or epic, list in experience order: Onboarding before Selfcare, not by sitemap or technical order.

## What each lens produces at discovery

| Lens | Fidelity | Output |
| --- | --- | --- |
| Stories | story_map | Epic → SubEpic → Story hierarchy with thin slices |
| DDD | bounded_context | Context map with aggregates and dependency arcs |
| UX | ia | Screen index with transitions and named regions |
| Clean Engineering | modules | Module map with one-way deps and build order |
| BDD | — | Not active at discovery |

## Theme ordering thinking

Don't order themes by architecture or technology stack. Order by what the user experiences first. If they onboard before they browse, Onboarding comes before Catalog. If they sign up before they subscribe, Sign Up comes before Manage Subscription.
