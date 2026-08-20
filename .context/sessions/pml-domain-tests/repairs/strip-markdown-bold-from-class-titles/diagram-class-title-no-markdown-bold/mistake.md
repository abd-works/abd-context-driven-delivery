# diagram-class-title-no-markdown-bold

- **entry_id:** c96dd33c
- **artifact:** tests/domain/.context/domain-model.drawio
- **rule:** (diagram) class-title-no-markdown-bold
- **wrong:** Class titles contain ** markdown bold notation baked into the label text (e.g., "**Prospect**", "**Subscriber**", "**Customer**"). The draw.io cell value uses HTML bold tags wrapping text that already includes the ** characters, doubling up and displaying the asterisks visibly. Class names should be plain text — the bold rendering is handled by the HTML <b> tag already present in the cell value.
- **status:** fixed
