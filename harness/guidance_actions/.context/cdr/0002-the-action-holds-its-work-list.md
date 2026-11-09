# A guidance action holds its work list; what the action keeps

The round-9 review (harness core, row 6) found *GuidanceAction* kept what it works on in loose fields beside its session, log and hook jobs (43 methods, total complexity 131), with fall-backs to the action it was started inside.

## Decision

- What an action works on is one part, *WorkList* (`action.work`), made with the action, and made inside the outer action's list for an action started inside another. It reads the guidance argument once (`take`), takes what another action listed (`take_listed`) or one fidelity (`take_fidelity`), and answers `listed`, `practice_set`, `practice_of` and `fidelity_of`. A list made inside another asks that list for the practices and fidelities it names none of itself, so the action no longer holds its outer action.
- The action keeps `listed`, `fidelity_of`, `practice_of`, `practice_slugs` and `work_on_fidelity` as its own verbs, each one line asking its list: recipes, the actions in `cdd_guidance/actions` and their specs name these verbs on the action, and they are what an action says it works on.
- After the split *GuidanceAction* has 36 methods and total complexity 90: under the complexity limit, over the method limit. What remains is one job, running an action for a call: the session and graph it works in, the log lines it writes, the recipes it publishes (`begin`, `act_quickly`, `session_context`) and the rules hook. The next step, if the method count is to fall further, is the session context and log lines (`session_context`, `_worked_fidelities`, `_worked_output`, `_session_practice`, `log_running`, `_log`) as a part made from the action's session and its list.
