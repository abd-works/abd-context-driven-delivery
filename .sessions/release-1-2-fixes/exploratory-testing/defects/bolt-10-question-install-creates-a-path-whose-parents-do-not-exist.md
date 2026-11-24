# Question: an install into a path whose parent folders do not exist creates them without a word

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt
**Story:** no scenario covers this.
**Module and class:** harness/installation/installer.py Installer.create / the file installations' mkdir(parents=True)
**Severity:** answered question

**Steps:** Installer.create('VS Code', C:/dev/_et/bolt/work/does/not/exist/.github, repo=...).install()

**Actual:** OK; does/not/exist/.github is made with 204 files. module-context.md says 'Install into an IDE folder that exists'. A mistyped --path makes a new folder tree instead of a refusal.

**Expected:** not known; is this intended?

**Tier that should catch it:** to be decided with the answer.

## Answer (2026-11-23)

An install whose IDE folder's parent does not exist is refused with `NotAnInstallFolder`, naming the missing folder, before anything is written; the IDE folder itself is still made. Built in `harness/installation/install_target.py` (`InstallTarget.__init__`); tested by `harness/installation/install_target_spec.py` ("whose parent folder does not exist", "missing, in a folder that exists") and `scripts/install_spec.py` ("with a path whose parent folder does not exist", exit 2); scenarios "Refuse a path whose parent folder does not exist" and "Make the IDE folder itself" in `story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md`.
