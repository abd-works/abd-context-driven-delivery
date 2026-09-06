# Rule: Scenarios cover all cases implied by the story

A solid story has at least one **happy path** scenario plus **edge** and **error** cases that trace to formal acceptance criteria, story text, notes, or agreed rules. If validation, persistence, or error handling matters, scenarios should show those outcomes explicitly — not assume "we'll handle errors somewhere."

## DO

- Include at least one success path with realistic data.
- Add boundary or rule-adjacent cases when limits, optional fields, or transitions are stated.
- Add failure paths with the observable error or prevention behavior (message, status, no persistence).

Plain scenario examples:
``Scenario: Valid payment amount is accepted
  When the **User** *Jane Doe* enters a **Payment Amount** of *$10,000.00 USD*
  Then the **Wire Payment** is marked as *successful*

Scenario: Amount over limit is rejected
  When the **User** *Jane Doe* enters a **Payment Amount** of *$500,000.01 USD*
  Then the **Wire Payment** is *rejected*
  And no **Wire Payment** record is created
``
## DON'T

- Ship only "everything works" scenarios when failures or edge cases are known.
- Describe errors abstractly ("invalid data") without the concrete violating example.
