---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Install Markdown Files

> Evidence: written on 2026-11-19 from the defects exploratory testing round 1 confirmed in install
> (`.sessions/release-1-2-fixes/exploratory-testing/defects/bolt-*.md`). Each scenario states a behaviour a source
> already promised; the source is named in the story's evidence. The stories of this sub-epic that had no confirmed
> defect have no scenarios here yet.

## Story: Store Install State

### Evidence

| Source | Note |
|--------|------|
| `harness/installation/.context/module-context.md` | "`/clean` removes what it wrote"; "one server installs many projects" |
| `harness/installation/installer.py` *ToolsetInstallFailed* | the install stops "so no IDE folder is left with part of a toolset" |
| bolt-01, bolt-03, bolt-06, bolt-13 | the defects each scenario closes |
| `harness/installation/install_record_spec.py`, `install_lock_spec.py`, `install_target_spec.py` | unit tier |
| `harness/installation/install_record_heavy_spec.py` | heavy tier: the real installer, and two installs in two processes |

#### Scenario: Clean one IDE folder after another was installed into

*Given* shop has CDD installed into shop/.cursor  
  *And* CDD is then installed into shop/.claude  
*When* the Person cleans shop/.cursor  
*Then* the files the install wrote into shop/.cursor are removed  
  *And* the install in shop/.claude is left as it is

#### Scenario: Keep the install folder as its whole path

*Given* the Person works in C:/work/shop  
*When* the Person installs CDD into the path .claude  
*Then* the record in C:/work/shop/.claude names the folder C:/work/shop/.claude  
  *And* a clean run from any other directory removes the files that install wrote

#### Scenario: Know the files of an install that stopped halfway

*Given* an install into shop/.cursor has written the generate skill  
*When* the install stops at a toolset it cannot publish  
*Then* the record in shop/.cursor lists the generate skill  
  *And* a clean of shop/.cursor removes it

#### Scenario: Run two installs into one folder at the same moment

*Given* shop/.cursor holds a finished install  
*When* two installs into shop/.cursor start at the same moment  
*Then* the second waits for the first  
  *And* both finish  
  *And* every file the record lists is in shop/.cursor

#### Scenario: Refuse an install while another outlasts the wait

*Given* an install is running in shop/.claude as process 4812  
*When* a second install into shop/.claude has waited as long as it waits  
*Then* the second is refused, naming shop/.claude and process 4812

#### Scenario: Take over the lock a stopped install left

*Given* shop/.claude holds the lock of an install whose process is gone  
*When* the Person installs CDD into shop/.claude  
*Then* the install runs

## Story: Choose Where To Install

### Evidence

| Source | Note |
|--------|------|
| `scripts/install.py --help` | "IDE name: Cursor, VS Code, Kilo, or Claude" |
| `scripts/install.py` `_chat_folder_refusal` | a chat folder that is no project is refused with exit 3, so the board mod stays quiet at chat start |
| bolt-02, bolt-04, bolt-11 (the empty name only) | the defects each scenario closes |
| `harness/installation/ide_layout_spec.py`, `install_target_spec.py`, `scripts/install_spec.py` | unit tier |

#### Scenario: Name the IDE in another case

*Given* shop has no CDD installed  
*When* the Person installs CDD for the IDE claude  
*Then* CDD is installed for Claude, into shop/.claude

#### Scenario: Refuse a name that is no IDE

*Given* shop has no CDD installed  
*When* the Person installs CDD for the IDE Emacs  
*Then* the install is refused, naming Emacs and the names it can be: Cursor, VS Code, Kilo, Claude  
  *And* nothing is written

#### Scenario: Refuse a file as the path

*Given* shop/README.md is a file  
*When* the Person installs CDD into the path shop/README.md  
*Then* the install is refused, saying shop/README.md is a file  
  *And* nothing is written

#### Scenario: Refuse an empty path

*Given* a script passes an unset variable as the path  
*When* it installs CDD into the path ""  
*Then* the install is refused, saying the path is empty  
  *And* nothing is written into the directory the script runs in

#### Scenario: Refuse a chat whose folder is not known

*Given* a chat starts with no folder known  
*When* the board mod installs CDD for the chat's folder ""  
*Then* the install is refused with exit 3, saying the chat's folder is not known

## Story: Refresh The Installer's Own Commands

### Evidence

| Source | Note |
|--------|------|
| `scripts/install.py --help`, `--self` | "Deploy only the Installer toolset (slash /install and /clean, hooks)" |
| `harness/installation/installer.py` `Installer.install` | "Installer-only refresh (`/install` and `/clean` without walking the catalog)" |
| bolt-14 | the defect the scenario closes |
| `scripts/install_spec.py` | unit tier |
| `harness/installation/install_record_heavy_spec.py` | heavy tier |

#### Scenario: Refresh the Installer's commands over a finished install

*Given* shop/.cursor holds a finished install with the generate skill  
*When* the Person runs the install with --self  
*Then* the install and clean commands are written again  
  *And* the generate skill is still in shop/.cursor  
  *And* the record still lists it, so a clean removes it

## Story: Install The Latest Release

### Evidence

| Source | Note |
|--------|------|
| `scripts/install.py` `_install_from_latest` | "A checkout already at or past that release merges nothing and keeps its own commits" |
| `scripts/install.py` `_match_release_version` | "a local edit to the version line ... is put back to the release's" |
| bolt-16 | the defect the second scenario closes |
| `scripts/install_heavy_spec.py` | heavy tier, with real git |

#### Scenario: Put a locally edited version back to the release's

*Given* the checkout is at release v1.2.0  
  *And* its pyproject.toml version line is edited to 9.9.9 and not committed  
*When* the Person installs from the latest release  
*Then* the version line reads 1.2.0 again

#### Scenario: Keep a committed version that is past the release

*Given* the checkout is past release v1.2.0  
  *And* it has committed version 1.3.0 in pyproject.toml  
*When* the Person installs from the latest release  
*Then* the version line still reads 1.3.0  
  *And* pyproject.toml is not modified

## Story: Publish Mods For Every Chat

### Evidence

| Source | Note |
|--------|------|
| bolt-12 | two installs at the same moment, from the main checkout and a ticket's worktree, both copy the mods into the one `claude-plugins` folder of the cdd home, and one fails with WinError 32 |
| `harness/mcp/claude_marketplace.py` `ClaudeMarketplace.publish_mods` | the owner of that folder: one install publishes into it at a time |
| `harness/mcp/cdd_home_heavy_spec.py` | heavy tier: four real processes publishing into one cdd home |

#### Scenario: Install from the main checkout and a ticket's worktree at the same moment

*Given* the stable lane serves the main checkout and the dev lane serves checkout-flow's worktree  
*When* an install from each starts at the same moment  
*Then* both finish  
  *And* the cdd home's marketplace holds the board mod whole
