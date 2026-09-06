---
scanner: channel-specific-language
---

# Rule: Use channel-specific language

**Scanner:** `scanners/channel-specific-language-scanner.py` — **`ChannelSpecificLanguageScanner`**

Prefer concrete CLI, Panel, or API surface detail over generic "Bot/System" wording when the product has distinct channels.

## DO

- Include concrete examples: `cli.` paths, quoted UI labels, explicit panel copy.

## DON'T

- Rely on generic "Bot …" steps without concrete syntax or UI cues (scanner warns).
