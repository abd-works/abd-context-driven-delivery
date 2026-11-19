# Question: an install into a path whose parent folders do not exist creates them without a word

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt
**Story:** no scenario covers this.
**Module and class:** harness/installation/installer.py Installer.create / the file installations' mkdir(parents=True)
**Severity:** question

**Steps:** Installer.create('VS Code', C:/dev/_et/bolt/work/does/not/exist/.github, repo=...).install()

**Actual:** OK; does/not/exist/.github is made with 204 files. module-context.md says 'Install into an IDE folder that exists'. A mistyped --path makes a new folder tree instead of a refusal.

**Expected:** not known; is this intended?

**Tier that should catch it:** to be decided with the answer.
