# prompt echo

- **`show_ide_toast` joins same-burst inject lines.** `chat edit → rules : agent bdd` then `chat edit → rules : clean engineering code, ddd tactics` becomes one toast with one `rules :` prefix. A later matching glob must not overwrite an earlier Guidance.
- **The IDE toast watches every workspace folder** for `.cursor/prompt-echo-toast.json`. Write the notice into each `workspace_roots` folder from the hook payload so it shows no matter which folder the file lives in.
