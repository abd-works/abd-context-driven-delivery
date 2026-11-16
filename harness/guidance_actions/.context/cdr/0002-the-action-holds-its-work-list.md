# A guidance action holds its work list; what the action keeps

The round-9 review (harness core, row 6) found *GuidanceAction* kept what it works on in loose fields beside its session, log and hook jobs (43 methods, total complexity 131), with fall-backs to the action it was started inside.

## Decision

- What an action works on is one part, *WorkList* (`action.work`), made with the action, and made inside the outer action's list for an action started inside another. It reads the guidance argument once (`take`), takes what another action listed (`take_listed`) or one fidelity (`take_fidelity`), and answers `listed`, `practice_set`, `practice_of` and `fidelity_of`. A list made inside another asks that list for the practices and fidelities it names none of itself, so the action no longer holds its outer action.
- The action keeps `listed`, `fidelity_of`, `practice_of`, `practice_slugs` and `work_on_fidelity` as its own verbs, each one line asking its list: recipes, the actions in `cdd_guidance/actions` and their specs name these verbs on the action, and they are what an action says it works on.
- After the split *GuidanceAction* has 36 methods and total complexity 90: under the complexity limit, over the method limit. What remains is one job, running an action for a call: the session and graph it works in, the log lines it writes, the recipes it publishes (`begin`, `act_quickly`, `session_context`) and the rules hook. The next step, if the method count is to fall further, is the session context and log lines (`session_context`, `_worked_fidelities`, `_worked_output`, `_session_practice`, `log_running`, `_log`) as a part made from the action's session and its list.

## Update

- `work_on_fidelity` is gone from the action: its one caller, *FidelityActionRunner* in this module, hands the fidelity to the action's list (`action.work.take_fidelity`) directly. Nothing outside this module called it.
- The verbs this record keeps stay on the action (`listed`, `fidelity_of`, `practice_of`, `practice_slugs`). What it does not cover moved into parts: running an operation once per listed guidance at its fidelity, and the rules each listed guidance holds the agent to, are the list's (`action.work.each`, `at_fidelity`, `rules_to_follow`); the files a call names and the action writes are *ActionFiles* (`action.files.path_named`, `read`, `wrote`); `source_label` is a function of the module. The hooks only an action's subclasses use are protected: `_made_for` and `_tool_inside`, which lists another action as a tool in place of `as_tool`.

- The version-1 refactoring moved the session context and the overlay rules into a part of their own, *SessionBrief* (`action.brief`), and renamed `_session_practice` to `session_practice`, which the brief and Validate ask.
