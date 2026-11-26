# Question: make_repository on a plain subfolder inside a repository makes a nested repository

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt
**Story:** no scenario covers this.
**Module and class:** space/repo/new_repository.py NewRepository.is_repository (looks only for <root>/.git/HEAD)
**Severity:** answered question

**Steps:** NewRepository(C:/dev/_et/bolt/work/one-commit/sub/inner).make_from_folder(), where one-commit is a repository and sub/inner holds a.txt.

**Actual:** Answers 'Created ... on main with a first commit'; the outer repository then shows '?? sub/' and cannot add the inner files. Should it refuse a folder that is inside another repository?

**Expected:** not known; is this intended?

**Tier that should catch it:** to be decided with the answer.

## Answer (2026-11-23)

Making a repository inside another repository's checkout is refused (`FolderInsideARepositoryError`, naming the folder and the repository that holds it) before anything is written. Built in `space/repo/new_repository.py` (`NewRepository._existing`); tested by `space/repo/new_repository_spec.py` ("a plain folder inside another repository's checkout") and `space/repo/new_repository_heavy_spec.py` ("a folder made a git repository" / "inside a subfolder of another repository", real git); scenario "Refuse a folder inside another repository" in `story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md`.
