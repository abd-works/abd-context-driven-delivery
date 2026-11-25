# Rendered markdown shows a file's front matter as a bold heading above its title

**Charter:** Round 3 second pass, Pixel: how each file of the combined project is displayed (check 3).
**Tester:** Pixel

**Story:** Review Generated Work In File Viewer / View Files In Source View / View File In Source View / Scenario "Render a markdown file as the page it describes". No scenario covers front matter.

**Module and class:** `harness/files_app/app/files/file-rendering.ts`, `renderingOf` (this file is the other chat's Rendered / Source work, committed as aa23b0968).

**Severity:** cosmetic (every generated practice file starts with front matter, so every rendered story map, scenario file and model opens on it).

**Steps**
1. Stack as in r3-pixel-01. Open the Files app on the sandbox, All session files, press `story-map.md` (`.context/story-map.md`), which starts
   ```
   ---
   fidelity: [discovery]
   artifact: [story-map]
   format: md
   ---
   ```

**Expected:** the front matter left out of the page, or shown small as the file's facts; the page's first heading is "Story Map - Bookshop".

**Actual:** (screenshots `C:\dev\_et\round3\pixel\shots\a2-all-folders.png`, `w17-.context_domain-model.md.png`) a rule, then **fidelity: [discovery] / artifact: [story-map] / format: md** as three (domain-model.md: four, with `extends: practices/clean_engineering/templates/class-model.md`) lines of one second-level heading, in larger type than every heading but the title: marked reads `---` under the lines as a heading underline.

**Tier that should catch it:** unit, `files/file-rendering.spec.ts`; no example there starts with front matter.
