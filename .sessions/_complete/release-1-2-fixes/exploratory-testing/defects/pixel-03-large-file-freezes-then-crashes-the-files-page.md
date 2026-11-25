# Opening a large file freezes the Files page, and a file of four megabytes crashes its tab: every line of the file is drawn at once

- **Charter:** Round 1 - explore the Files app and the board's pages in a real browser as a person whose files change under the page
- **Tester:** Pixel
- **Story:** Review Generated Work In File Viewer > Open Files In Files App. No scenario covers a large file.
- **Module and class:** `harness/files_app/app/files/file-source-view.tsx` (the open file's Monaco editor). The editor is as tall as its whole file, so Monaco draws every line: `document.querySelectorAll('.view-lines .view-line').length` answers 90001 for a file of 90,000 lines, where an editor with a fixed height draws only the lines in sight.
- **Severity:** blocks work (the tab dies, and with it every open file and unsent comment on the page)

## Steps

Sandbox: `C:\dev\_et\pixel\work\repo`, branch and session `pixel-files`; Files server on 8902; scripts `C:\dev\_et\pixel\work\scripts\t4.py` (four megabytes) and `t6.py` (one megabyte).

1. Write `src/big.py`: 120,000 times `def f<i>():\n    return <i>\n\n` (4,217,780 bytes, 360,000 lines). Write `src/medium.py` the same way with 30,000 (about one megabyte, 90,000 lines). Commit both on `pixel-files`.
2. Open `http://127.0.0.1:8902/?files=pixel-files&fidelity=stories-story-map,clean-engineering-code,stories-acceptance-tests&project=C:\dev\_et\pixel\work\repo`, press **All session files**, turn the code format filter off.
3. Press `big.py`. In a second run press `medium.py`.

## Expected

The file opens, or the page says the file is too large to show. The other files stay usable.

## Actual

- `big.py`: the server answers the file in 5.1 seconds (`session/.../file`, 4,217,910 bytes), then the page answers nothing for 160 seconds and Chromium reports `Target crashed`. An earlier run that pressed each listed file in turn stopped for good at `big.py` (no screenshot could be taken).
- `medium.py`: the file shows, with 90,001 line elements in the page; a one-line script in the page then takes 8, 8.5 and once 15.8 seconds to answer.

Headless Chromium from Playwright, 1600 by 900. A person's browser may hold out longer before it crashes; the count of line elements is the same.

## Tier that should catch it

e2e: only Monaco in a real browser draws lines, and the unit specs stub the editor. No spec opens a file longer than a few dozen lines.

## Also seen by

## Confirmation (Rivet, round 2)
- Result: confirmed
- What I ran and saw: my own stack (`pstack2.py`: cdd server on 8913, Files server on 8914, headless Chromium, 1600 by 900). `medium.py` (90,000 lines): shown after 15.1 s with 90,001 `.view-line` elements, and a script of one word in the page then took 12.6 s to answer. `big.py` (360,000 lines; 3,857,780 bytes with LF line ends, where the report's 4,217,780 is the same text with CRLF): the page answered nothing for 373.9 s and Chromium raised its crash event.
- Cause, if you found it: not looked into beyond the report's own: the count of 90,001 line elements agrees with `harness/files_app/app/files/file-source-view.tsx` drawing an editor as tall as its file.
- Shares its cause with: none
