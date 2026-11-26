# A practice turned off in the Files app while no stage is selected narrows neither the file list nor the graph view: its files and its whole practice tree stay

- **Charter:** Round 3, second pass - explore the Files app's graph view on the combined project in a real browser (checks 5 and 6)
- **Tester:** Lens
- **Story:** Review Generated Work In File Viewer > Filter Files In Files App > Follow Chat Bar Selection In Files App, and Explore Graph In Files App (`harness/files_app/.context/module-context.md`: "the stage, practice, format and Changed filters narrow both alike"). The chip's own title reads "CE: on, press to turn it off here and on the chat bar". No scenario covers a practice turned off with no stage selected.
- **Module and class:** `harness/files_app/app/files/files-page.ts` `listedBy` (`selection?.is_stage_chosen ? selection.fidelities : linked`: with no stage chosen the fidelities listed are the link's, whatever practices are on), used by `filesShown` and `rootFilesShown`. Not among the files another chat was editing (`files-page-view.tsx` draws the chip; the rule is in `files-page.ts`).
- **Severity:** wrong result

## Steps

Sandbox `C:\dev\_et\round3\lens\work`, session `main`, five practices on, no stage selected (the state the page opens in); scripts `C:\dev\_et\round3\lens\drv\w10.py` and `w11.py`.

1. Open the Files app with every fidelity, press **All session files**, press **Graph**: 84 files are read, five practice trees show.
2. Press the **CE** chip. It shows off (`aria-pressed="false"`).
3. Press it on again; select the three stages (Discovery, Specification, Implementation); press **CE** off again.

## Expected

After step 2 the files of Clean Engineering's fidelities leave the list, the graph is read again without them, and the clean_engineering tree leaves the graph view, as it does in step 3.

## Actual

- Step 2: no `graph-trees` call follows, the list still holds the same 84 files (all of `src/`), and the clean_engineering tree still shows its 7 packages. The same for Stories, DDD and BDD turned off, one or two at a time: nothing changes.
- Step 3, the same chip with the three stages selected: the list drops to 53 files (the 31 under `src/` that are Clean Engineering's go), the graph is read again and shows `stories, ddd, ux, bdd`.
- So the practice chips work only once a stage is selected, and the stage toggles' own titles say that none selected shows every stage.

Screenshots: `C:\dev\_et\round3\lens\shots\32-ce-off.png` (CE off, its tree and files still there), `33-three-stages-ce-off.png`.

## Tier that should catch it

Unit (`harness/files_app/app/files/files-page.spec.ts`): `listedBy` is specified for a stage chosen and for none, but no example turns a practice off with none chosen and asks what is shown.

## Also seen by
