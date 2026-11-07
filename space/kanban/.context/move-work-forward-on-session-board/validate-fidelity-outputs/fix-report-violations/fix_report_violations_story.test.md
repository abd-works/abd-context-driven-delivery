# (E) Move Work Forward On Session Board
## (E) Validate Fidelity Outputs
### (S) Person --> Fix Report Violations

#### Scenario: Fix one violation at its line

*Given* checkout-flow's story_map report lists verb-noun-format at .context/story-map.md line 6
*And* a chat is connected
*When* the Person fixes that violation
*Then* the chat receives one message naming the verb-noun-format rule, the error at .context/story-map.md:6, and the content that failed, with instructions to fix it

#### Scenario: Fix every violation of a rule

*Given* checkout-flow's story_map report lists verb-noun-format
*When* the Person fixes every violation of verb-noun-format
*Then* the chat receives one message with every verb-noun-format violation, each at its file and line with the content that failed, and instructions to fix them

#### Scenario: Fix every violation in the report

*Given* checkout-flow's report lists violations of verb-noun-format and do-not-invent-requirements
*And* a chat is connected
*When* the Person fixes every violation in the report
*Then* the chat receives one message naming each rule with every violation of it, each at its file and line with the content that failed, and instructions to fix them all

#### Scenario: Read an open report again after the fix

*Given* checkout-flow's story_map report is open with verb-noun-format listed
*When* Claude Code validates the story map again with no violations
*Then* the open report lists no rules
