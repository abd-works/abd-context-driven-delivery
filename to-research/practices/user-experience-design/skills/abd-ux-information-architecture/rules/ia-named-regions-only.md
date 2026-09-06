# Rule: IA per screen lists named regions only — no controls

**Scanner:** AI review

The information-architecture layer on a screen lists the named regions of that screen and nothing else. Each region label is a term from the domain-language file. Controls (buttons, inputs, dropdowns, checkboxes), copy strings, field placeholders, and any wireframe-level detail are out of scope for this skill and belong in `abd-lo-fi`.

## DO

- List regions as a flat, separator-delimited row of UL terms.

  **Example (pass):**
  ```
  [ crowd manager ]
    IA: crowd tree panel | toolbar | filter bar | character detail panel | status bar
  ```
  where every named region is defined in the UL file.

- Stop at the level of "named container a user perceives as a distinct surface".

  **Example (pass):**
  ```
  [ game directory prompt ]
    IA: prompt panel | path input area | error message area | continue control area
  ```
  Region names indicate areas, not specific controls inside them.

## DO NOT

- Name a control as if it were a region.

  **Example (fail):**
  ```
  [ game directory prompt ]
    IA: prompt panel | "Browse..." button | "Continue" button | text input field
  ```
  These are controls; they belong in `abd-lo-fi`, not the site map.

- Embed copy strings or labels-as-content.

  **Example (fail):**
  ```
  [ game directory prompt ]
    IA: "COH game directory not found or invalid" message | path input
  ```
  Copy belongs to lo-fi. The IA names the message *area*, not its content.

- Indicate ordering, sizing, or layout.

  **Example (fail):**
  ```
  [ crowd manager ]
    IA: 1. crowd tree panel (left, 300px) | 2. toolbar (top) | ...
  ```
  Position and size are wireframe concerns, not IA.
