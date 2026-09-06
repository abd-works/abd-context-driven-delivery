### Rule: A package's listed operations share one subject

A package-tier context file is justified only when the listed operations belong together — they manipulate the same concept, talk to the same external system, or implement the same well-named capability. A "package" whose operations span unrelated subjects is a grab-bag and should be re-classified as miscellaneous (grab-bag flavour); promoting it to package gives it false coherence and the documentation lies. Passing means the package can be described in one sentence without using "and" to join unrelated concerns. Failing means the operation list reads like a junk drawer that happens to share a folder.

#### DO

- Describe the package as one named subject around a single noun.

  **Example (pass):**
  ```markdown
  # Package: Zendesk

  Zendesk is the ticket client. All operations build payloads for
  customer-lifecycle events, post tickets to the Zendesk API, or look up
  ticket status. Consumers: Mavenir controllers only.

  **Public surface**
  - `createTicket(input)` — opens a new support ticket.
  - `closeTicket(id, resolution)` — marks an existing ticket resolved.
  - `findByCustomer(customerId)` — returns the ticket history.
  ```

- When operations cluster into two unrelated groups, split into two packages and write two context files.

  **Example (pass):** What started as a package called "Customer" containing `formatPhone()`, `validateEmail()`, `loadFromMavenir()`, `sendWelcomeEmail()` is split into a Mavenir wrapper package and a Customer validation package.

#### DO NOT

- Document a package whose operations span unrelated subjects.

  **Example (fail):**
  ```markdown
  # Package: Utils

  - `formatDate(date)` — formats a date for display.
  - `validateEmail(s)` — checks email shape.
  - `parseJWT(token)` — decodes a JWT.
  - `retryWithBackoff(fn)` — retries a function.
  - `escapeHtml(s)` — escapes HTML.
  ```
  Five concerns, no shared subject. This is a grab-bag; document it with the miscellaneous template and list each utility with its real owner.

- Hide a grab-bag behind a vague package name.

  **Example (fail):** A package called "Helpers" with eleven unrelated methods. "Helpers" is not a subject; the package surface is the concatenation of every developer's pet utility.

**Source:** Cohesion is what makes a package a unit — operations that do not share a subject share only a folder, and the documentation should say so by classifying the folder as miscellaneous.
