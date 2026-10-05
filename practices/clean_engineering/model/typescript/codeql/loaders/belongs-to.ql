/**
 * @name Practice graph belongs-to
 * @kind problem
 * @id cdd/practice-graph/belongs-to
 */

import javascript
import subject_filter

from ClassDefinition cls, string mod
where
  inSubject(cls) and
  mod = cls.getFile().getRelativePath().regexpCapture("src/([^/]+)/.*", 1)
select cls.getName(), mod, cls.getLocation().getStartLine(), "true",
  cls.getFile().getRelativePath()
