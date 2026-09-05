# Rule: Screen names use domain terms verbatim

**Scanner:** AI review

Every screen box label on the site map is a term that appears in the supplied domain-language (UL) file, copied character-for-character. Paraphrased, abbreviated, or invented names are a fail. The UL file is the single source of truth for screen names; the site map mirrors it.

## DO

- Use the exact term from the UL file as the screen label.

  **Example (pass):**
  ```
  [ crowd manager ]
  ```
  where the UL file defines `crowd manager — the pre-session library surface where the GM creates, organizes, browses, and persists crowds and characters`.

- When the UL does not yet name a screen the stories require, stop and ask for a UL term to be added before drawing.

  **Example (pass):**
  > "The story 'Validate City of Heroes Game Directory' implies a screen with no UL name. Should we add 'game directory prompt' to the UL?"

## DO NOT

- Invent a label that is not in the UL file.

  **Example (fail):**
  ```
  [ Character Roster Window ]
  ```
  when the UL defines `crowd manager`, not "Character Roster Window".

- Paraphrase or abbreviate a UL term.

  **Example (fail):**
  ```
  [ crowd mgr ]
  ```
  when the UL defines `crowd manager`.

- Substitute a technical name for a domain name.

  **Example (fail):**
  ```
  [ MainShellView ]
  ```
  when the UL defines `crowd manager`.
