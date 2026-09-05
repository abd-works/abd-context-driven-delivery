# Rule: Two trailing spaces on every scenario line

Every line inside a Given/When/Then block ends with two spaces (`  `) so markdown renderers produce a visible line break instead of collapsing the step onto the previous line.

**DO** add two trailing spaces to every step line — Given, When, Then, And, But — and every continuation indent.

  **Example (correct):**
  ```
  Given a **Campaign** *Summer Sale* is *active*  
    And a **Voucher** *SUMMER20* belongs to that **Campaign**  
  When the **API Client** submits **Voucher Code** *SUMMER20* with **Order Amount** *100.00*  
  Then a **Redemption** is recorded  
    And the **Discount Amount** is *20.00*  
  ```

**DO NOT** end step lines with a single space or no space — markdown preview collapses them into a single paragraph.

  **Example (wrong):**
  ```
  Given a **Campaign** *Summer Sale* is *active*
    And a **Voucher** *SUMMER20* belongs to that **Campaign**
  When the **API Client** submits **Voucher Code** *SUMMER20*
  Then a **Redemption** is recorded
  ```

**Applies to:** every `.md` file produced by this skill — `specification-by-example.md` and any named variant.

**Scanner:** string scan — flag any step line (`/^(Given|When|Then|And|But|\s+And|\s+But)/`) that does not end with two or more spaces before the newline.
