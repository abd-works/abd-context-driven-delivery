Fidelity: model + behavior

WorkSession
  guidance
  openTurn
  turn
    // /turn announces a new turn; increments turn age for inclusion and exclude
    // force a commit
    → turn.turn
      → turn._commit
        → git.commit

WorkSessionGuidance : PracticeGuidance
  rules
  // work guidelines file; rules section is a WorkSessionRulesCollection
  ----
WorkSessionRulesCollection : RulesCollection
  priorityInclusion
  relevantInclusion
  contextInclusion
  exclude
  priorityDetail
  relevantDetail
  contextDetail
  add workSessionRule
    // no matching base rule → insert new WorkSessionRule
    // matching base rule → add the example, 
    // star += 1, move up when highest star
    // guidance and fidelity may both be set, guidance only (practice-wide), or neither (global)
    _matching_work_session_rule
    _matching_practice_rule
      // → practiceGuidance.rules
    _place_by_star
  inject_rules
    // practice rules being injected this turn
    // called from HookServer after handlers merge
    // session rules of the same name overwrite; remaining injected rules at the bottom
    // changing inclusion, exclude, or detail leaves rules on the collection; the next inject_rules uses the new settings
    _matching_rules
      // match when rule.guidance is empty or equals that generate's guidance
      // and rule.fidelity is empty or equals that generate's fidelity
      // last fail at exclude turns ago or older → not injected
      // same match for specific, practice-wide, and global
    _merge_injected
      // session render first in star order; leftover injected markdown after
      _without_slugs
    _write_last_chat_injected
      // after additional_context is sent; overwrite last-chat-injected-rules.md
    _band
      // priority | relevant | context from inclusion counts and turn age
    _render
      // examples | body | slug
  ----
WorkSessionRule : Rule
  guidance
  fidelity
  star
  examples
    Example
      mistake
      correction
  // empty guidance and empty fidelity → global
  // guidance set, fidelity empty → practice-wide
  ----
Turn
  workSession
  mistakes
  correction
  record_mistake ★
    // to be implemented
  record_correction ★
    // to be implemented
    // later: → workSession.guidance.rules.add

---

Fidelity: behavior

a work session
  that is open
    that has generated output with clean engineering model
      that has a correction for put-logic-on-the-owning-resource
        workSession.guidance.rules.add(workSessionRule)
          → workSession.guidance.rules._matching_work_session_rule(workSessionRule)
          → workSession.guidance.rules._matching_practice_rule(workSessionRule)
            → practiceGuidance.rules
          → workSession.guidance.rules._place_by_star(workSessionRule)
          ← workSessionRule
        with a matching work session rule
          workSession.guidance.rules.add(workSessionRule)
            → workSession.guidance.rules._matching_work_session_rule(workSessionRule)
              ← matching workSessionRule
            → matching.examples.add(example)
            ← workSessionRule
          it should add the mistake to that work session rule
            — workSessionRule.examples
          it should raise that rule's star
            — workSessionRule.star
        with no matching work session rule and a matching practice rule
          workSession.guidance.rules.add(workSessionRule)
            → workSession.guidance.rules._matching_work_session_rule(workSessionRule)
              ← none
            → workSession.guidance.rules._matching_practice_rule(workSessionRule)
              → practiceGuidance.rules
              ← matching practice rule
            ← workSessionRule
          it should add a new work session rule tagged clean_engineering and code
            — workSessionRule.guidance
            — workSessionRule.fidelity
          it should have the same name as the matching practice rule
            — workSessionRule.slug
          it should attach the mistake and the correction
            — workSessionRule.examples
          it should add a star
            — workSessionRule.star
        with a matching practice rule that is shared across fidelities
          workSession.guidance.rules.add(workSessionRule)
            → workSession.guidance.rules._matching_work_session_rule(workSessionRule)
              ← none
            → workSession.guidance.rules._matching_practice_rule(workSessionRule)
              → practiceGuidance.rules
              ← matching practice rule
            ← workSessionRule
          it should add the new work session rule for clean engineering with no fidelity tag
            — workSessionRule.guidance
            — workSessionRule.fidelity
          it should attach the mistake and the correction
            — workSessionRule.examples
          it should add a star
            — workSessionRule.star
        with no matching guideline and no matching fidelity
          that belongs to a guideline and a fidelity
            it should create and then add a new work session rule and assign the correct guideline and fidelity
              workSession.guidance.rules.add(workSessionRule)
                → workSession.guidance.rules._matching_work_session_rule(workSessionRule)
                  ← none
                → workSession.guidance.rules._matching_practice_rule(workSessionRule)
                  → practiceGuidance.rules
                  ← none
                ← workSessionRule
              — workSessionRule.guidance
              — workSessionRule.fidelity
          that does not belong to a guideline and a fidelity
            it should create and then add a new work session rule and assign no guideline or fidelity
              workSession.guidance.rules.add(workSessionRule)
                → workSession.guidance.rules._matching_work_session_rule(workSessionRule)
                  ← none
                → workSession.guidance.rules._matching_practice_rule(workSessionRule)
                  → practiceGuidance.rules
                  ← none
                ← workSessionRule
              — workSessionRule.guidance
              — workSessionRule.fidelity
        with that rule having established priority from previous runs
          it should increase its priority by one
            workSession.guidance.rules.add(workSessionRule)
              → workSession.guidance.rules._matching_work_session_rule(workSessionRule)
                ← matching workSessionRule
              → workSession.guidance.rules._place_by_star(workSessionRule)
              ← workSessionRule
            — workSessionRule.star
          it should place the rule in the top rules section according to its new priority
            workSession.guidance.rules.add(workSessionRule)
              → workSession.guidance.rules._place_by_star(workSessionRule)
              ← workSessionRule
            — workSession.guidance.rules
    that has announced a new turn
      workSession.turn()
        → turn.turn()
          → turn._commit()
            → git.commit()
        ← turn
      that is generating with clean engineering code
        with practice rules being injected for clean engineering code
          practiceGuidance.rules.inject_rules()
            → workSession.guidance.rules.inject_rules()
              → workSession.guidance.rules._matching_rules()
                ← matching workSessionRules
              → workSession.guidance.rules._band(workSessionRule)
              → workSession.guidance.rules._render(workSessionRule, detail)
              ← matching workSessionRules
            ← matching workSessionRules
          it should match work session rules for shared practice and fidelity practice rules first in the injected set
            practiceGuidance.rules.inject_rules()
              → workSession.guidance.rules.inject_rules()
                → workSession.guidance.rules._matching_rules()
                  ← matching workSessionRules
          it should keep put-logic-on-the-owning-resource at the established priority
            — workSessionRule.star
          it should overwrite the injected rule of the same name
            practiceGuidance.rules.inject_rules()
              → workSession.guidance.rules.inject_rules()
                → workSession.guidance.rules._matching_rules()
                → workSession.guidance.rules._merge_injected()
                  → workSession.guidance.rules._without_slugs()
          it should put remaining injected rules at the bottom
            practiceGuidance.rules.inject_rules()
              → workSession.guidance.rules.inject_rules()
                → workSession.guidance.rules._merge_injected()
          it should write last-chat-injected-rules with the injected additional context
            practiceGuidance.rules.inject_rules()
              → workSession.guidance.rules.inject_rules()
                → workSession.guidance.rules._write_last_chat_injected()
          with a practice-wide work session rule
            it should inject that rule in the same star order as fidelity-specific rules
              practiceGuidance.rules.inject_rules()
                → workSession.guidance.rules.inject_rules()
                  → workSession.guidance.rules._matching_rules()
                    ← matching workSessionRules
          with a global work session rule
            it should inject that rule in the same star order as fidelity-specific rules
              practiceGuidance.rules.inject_rules()
                → workSession.guidance.rules.inject_rules()
                  → workSession.guidance.rules._matching_rules()
                    ← matching workSessionRules
          with a global rule that has more stars than a fidelity-specific rule
            it should place the global rule first
              practiceGuidance.rules.inject_rules()
                → workSession.guidance.rules.inject_rules()
                  → workSession.guidance.rules._matching_rules()
                    ← matching workSessionRules
        with practice rules being injected for a different fidelity
          practiceGuidance.rules.inject_rules()
            → workSession.guidance.rules.inject_rules()
              → workSession.guidance.rules._matching_rules()
                ← matching workSessionRules
            ← matching workSessionRules
          it should leave the clean_engineering code work session rules out of that reorder
          it should still inject practice-wide clean_engineering rules
          it should still inject global rules
        with priority inclusion set to 1
          with priority injection detail set to examples
            with a rule that failed last turn
              it should treat that rule as priority
                practiceGuidance.rules.inject_rules()
                  → workSession.guidance.rules.inject_rules()
                    → workSession.guidance.rules._band(workSessionRule)
                      ← priority
              with a new generation turn that matches the failed rule
                it should inject the full rule plus mistake and correction examples
                  practiceGuidance.rules.inject_rules()
                    → workSession.guidance.rules.inject_rules()
                      → workSession.guidance.rules._matching_rules()
                        ← matching workSessionRule
                      → workSession.guidance.rules._band(workSessionRule)
                        ← priority
                      → workSession.guidance.rules._render(workSessionRule, priorityDetail)
                        ← workSessionRule at priorityDetail
        with relevant inclusion set to 2
          with relevant injection detail set to examples
            with a rule that failed one turn earlier
              it should treat that rule as relevant
                practiceGuidance.rules.inject_rules()
                  → workSession.guidance.rules.inject_rules()
                    → workSession.guidance.rules._band(workSessionRule)
                      ← relevant
              it should inject the full rule plus mistake and correction examples
                practiceGuidance.rules.inject_rules()
                  → workSession.guidance.rules.inject_rules()
                    → workSession.guidance.rules._render(workSessionRule, relevantDetail)
                      ← workSessionRule at relevantDetail
        with context inclusion set to 3
          with context injection detail set to slug
            with exclude set to 5
              with a rule that failed previous turns inside the context window
                it should treat that rule as context
                  practiceGuidance.rules.inject_rules()
                    → workSession.guidance.rules.inject_rules()
                      → workSession.guidance.rules._band(workSessionRule)
                        ← context
                it should inject only the rule slug and its star
                  practiceGuidance.rules.inject_rules()
                    → workSession.guidance.rules.inject_rules()
                      → workSession.guidance.rules._render(workSessionRule, contextDetail)
                        ← workSessionRule at contextDetail
              with a rule that failed five turns ago
                it should leave that rule out of the prompt
                  practiceGuidance.rules.inject_rules()
                    → workSession.guidance.rules.inject_rules()
                      → workSession.guidance.rules._matching_rules()
                        ← without that workSessionRule
                it should keep that rule on the collection
                  — workSession.guidance.rules
        that has changed relevant inclusion to 1
          with a rule that failed one turn earlier
            it should treat that rule as context
            practiceGuidance.rules.inject_rules()
              → workSession.guidance.rules.inject_rules()
                → workSession.guidance.rules._band(workSessionRule)
                  ← context
                → workSession.guidance.rules._render(workSessionRule, contextDetail)
                  ← workSessionRule at contextDetail
        that has changed priority injection detail to slug
          with a rule that failed last turn
            it should inject only the rule slug and its star
              practiceGuidance.rules.inject_rules()
                → workSession.guidance.rules.inject_rules()
                  → workSession.guidance.rules._band(workSessionRule)
                    ← priority
                  → workSession.guidance.rules._render(workSessionRule, priorityDetail)
                    ← workSessionRule at priorityDetail
        that has changed exclude to 2
          with a rule that failed previous turns inside the context window
            it should leave that rule out of the prompt
              practiceGuidance.rules.inject_rules()
                → workSession.guidance.rules.inject_rules()
                  → workSession.guidance.rules._matching_rules()
                    ← without that workSessionRule
            it should keep that rule on the collection
              — workSession.guidance.rules
        that has changed exclude to 10
          with a rule that failed five turns ago
            it should treat that rule as context
            practiceGuidance.rules.inject_rules()
              → workSession.guidance.rules.inject_rules()
                → workSession.guidance.rules._band(workSessionRule)
                  ← context
            it should inject only the rule slug and its star
              practiceGuidance.rules.inject_rules()
                → workSession.guidance.rules.inject_rules()
                  → workSession.guidance.rules._render(workSessionRule, contextDetail)
                    ← workSessionRule at contextDetail
