# Two installs started at the same moment into one folder fail one of them with a raw FileNotFoundError while it cleans the previous install

**Charter:** Round 1 second charter - the install scripts and the lanes (card 89963ac5a974)
**Tester:** Bolt

**How it was run:** the real `scripts/install.py` from `C:\dev\_et\bolt\checkout-main`, isolated as in bolt-12.

**Story:** Register And Install Toolsets - no scenario has two installs run at once.

**Module and class:** `harness/installation/install_record.py` `InstallRecord.remove_installed` (`target.is_file()` then `target.unlink()`, with the other install removing the same files in between).

**Severity:** wrong result

**Steps:** in `checkout-main`, after one finished install: `python scripts/install.py --ide Claude & python scripts/install.py --ide Claude & wait`

**Expected:** both finish, or the second says another install is running in this folder.

**Actual:** one exits 0. The other exits 1 with a traceback ending
`FileNotFoundError: [WinError 2] The system cannot find the file specified: 'C:\\dev\\_et\\bolt\\checkout-main\\.claude\\skills\\builders-create-practice-guidance\\SKILL.md'`.
This time the folder ended whole (201 files recorded, all on disk), because the install that failed stopped in its clean. Nothing keeps the other order from happening: the second's clean removing files the first has just written. Seen once in one try. In real use: two chats opening in one project together, each running the board mod's install.

**Tier that should catch it:** heavy: no spec runs two installs at once into one folder.
