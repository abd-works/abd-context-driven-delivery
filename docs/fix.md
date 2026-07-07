
When errors are found by the user or an agent that should have been caught by a scanner or rule, *fix* the output through an iterative build and test loop until the output is clean. 

Run the *fix* loop as a background sub-agent so that the main conversation continues uninterrupted. 

Create the checlkist below and execute each item in the list; visibly strike off each task so the user / agent can confirm you performed every step.


- [ ]  **Understand the user's complaint exactly.** Ask for specifics if needed
   (which file, section, element, what is wrong). 
- [ ]  **Evaluate is the source a rule/scanner issue** if this is a scanner/rule issue proceed; else exit this flow and mark it *not applicable* / *done*.
- [ ] **Initialize sub agent with the following information**
    - Absolute path to the output file(s) being fixed
    - Rule data: Rule text, scanner, rule pass and fail examples
    - erroneous output, desired output
    - A clear instruction: apply **rules and scanner fix only** — do not rebuild guidance or api from scratch
    - Which parts of the output to touch and which to leave alone
Parent agent ends its turn immediately after launching. The sub-agent
notifies on completion.
- [ ] **Identify the source of error.** Read the relevant scanner(s) and rule(s) in
   `scanners/` and `rules/`. Determine why they missed it — wrong threshold,
   missing case, rule not codified, etc.
- [ ] **Create Run Space** - \run-n+1\ add *error source*, 
- [ ] **Fix the scanner and/or rule** until the combination of the two can flag the same problem the user identified. This may require:
   - Tightening a threshold in a scanner
   - Writing a new scanner file
   - Adding a new rule `.md` to `rules/`
- [ ] **Verify the rule and/or scanner now catches it.** Run rule `@enforce` on the original output; it must report a *FAIL* on the scanner ata minimum, but preferable both the scanner and the rule. Run rule `@enforce` on the corrected output; it must report a *PASS* on the rule and the scanner.



