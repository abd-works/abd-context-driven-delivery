# Question: make_repository on a plain subfolder inside a repository makes a nested repository

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt
**Story:** no scenario covers this.
**Module and class:** space/repo/new_repository.py NewRepository.is_repository (looks only for <root>/.git/HEAD)
**Severity:** question

**Steps:** NewRepository(C:/dev/_et/bolt/work/one-commit/sub/inner).make_from_folder(), where one-commit is a repository and sub/inner holds a.txt.

**Actual:** Answers 'Created ... on main with a first commit'; the outer repository then shows '?? sub/' and cannot add the inner files. Should it refuse a folder that is inside another repository?

**Expected:** not known; is this intended?

**Tier that should catch it:** to be decided with the answer.
