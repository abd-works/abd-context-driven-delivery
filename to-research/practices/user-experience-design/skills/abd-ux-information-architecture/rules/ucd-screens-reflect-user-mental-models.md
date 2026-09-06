# Rule: Screens and IA reflect the user's mental model, not the technical decomposition

**Scanner:** AI review

The screen graph and the IA per screen are organized around how the product owner and domain experts already talk and reason about the work, expressed in the Domain Language. Technical artifacts (services, modules, repositories, durable objects, modes, layers) are not screens, are not transitions, and are not region names. If a label only makes sense to an engineer reading code, it does not belong on this canvas.

## DO

- Anchor every label in the UL file and check it reads naturally to a domain expert.

  **Example (pass):**
  ```
  [ crowd manager ]
    IA: crowd tree panel | toolbar | filter bar | character detail panel | status bar
  ```
  Every term is something a GM would say while running a session.

- When the technical name and the domain name differ, pick the domain name.

  **Example (pass):** UL defines `crowd manager` as the user-facing surface; the code calls the same thing `MainShellViewModel`. The site map says `crowd manager`.

## DO NOT

- Name screens after services, classes, view models, modules, or durable objects.

  **Example (fail):**
  ```
  [ AgentDurableObject ]      [ CrowdRepositoryService ]
  ```
  These are infrastructure, not user-visible states.

- Name regions after technical layers (presenter, view-model, store).

  **Example (fail):**
  ```
  [ crowd manager ]
    IA: CrowdTreeViewModel | ToolbarPresenter | ContextMenuController
  ```
  Region names should describe what the GM perceives, not the wiring behind it.

- Organize screens around code modules rather than around user goals.

  **Example (fail):** Splitting one logical *crowd manager* screen into "crowd tree module" and "character detail module" because two different code modules render those panels.
