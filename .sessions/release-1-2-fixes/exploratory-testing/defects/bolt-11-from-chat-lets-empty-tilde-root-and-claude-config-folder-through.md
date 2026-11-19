# `--from-chat` refuses home, temp and spare folders however they are spelled, but lets through an empty folder name, `~`, a drive root, and Claude Code's own config folder

**Charter:** Round 1 second charter - the install scripts and the lanes (card 89963ac5a974)
**Tester:** Bolt

**How it was run:** `C:\dev\_et\bolt\refuse.py` loads `scripts/install.py` from a copy of the build and calls `_chat_folder_refusal` and `_install_path` with each spelling, with home and `CLAUDE_CONFIG_DIR` in the sandbox. The decision only: no install was run for these.

**Story:** Register And Install Toolsets - install into a chat's own folder refuses the home folder, the temporary folder, and the desktop app's spare folders (`scripts/install.py` `_chat_folder_refusal`). No scenario covers the folders below.

**Module and class:** `scripts/install.py` `_chat_folder_refusal` and `_install_path`.

**Severity:** wrong result (empty name); question (the others)

**Steps:** `cd C:\dev\_et\bolt\work`, then `python ../refuse.py`.

**Expected:** a folder that is no project is refused with exit 3, so the board mod stays quiet at chat start.

**Actual:** refused correctly (27 spellings tried): home, temp and spare with a trailing slash, upper and lower case, forward slashes, `\.`, `x\..`, an 8.3 short name, a subfolder of temp, a missing subfolder of temp or of spares, and a junction to home or to a temp subfolder. Let through:

| `--from-chat` | installs into |
|---|---|
| `""` (a chat whose folder is not known) | `<current directory>\.claude` |
| `.` | `<current directory>\.claude` |
| `~` (not expanded) | `<current directory>\~\.claude` |
| `C:\` | `C:\.claude` |
| `<home>\.claude` (Claude Code's config folder) | `<home>\.claude\.claude` |
| `C:\Windows\Temp` (a temporary folder that is not this user's) | `C:\Windows\Temp\.claude` |

A folder that does not exist is not checked either; the install makes it (see bolt-10).

**Tier that should catch it:** unit (`scripts/install_spec.py`): its examples name the home, temp and spare folders by their plain paths only.
