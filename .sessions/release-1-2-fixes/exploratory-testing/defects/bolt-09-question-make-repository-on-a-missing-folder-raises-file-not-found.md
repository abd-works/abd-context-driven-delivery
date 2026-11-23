# Question: make_from_folder on a folder that does not exist raises a raw FileNotFoundError, though create says it makes the folder first

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt
**Story:** no scenario covers this.
**Module and class:** space/repo/new_repository.py NewRepository.make_from_folder (write_ignores runs before create makes the folder)
**Severity:** question

**Steps:** NewRepository(C:/dev/_et/bolt/work/brand-new).make_from_folder()

**Actual:** FileNotFoundError: [Errno 2] No such file or directory: '...brand-new\.gitignore'. Can repo.make_repository ever be given a folder that is not there?

**Expected:** not known; is this intended?

**Tier that should catch it:** to be decided with the answer.
