/**
 * @name Practice graph modules
 * @kind problem
 * @id cdd/practice-graph/modules
 */

import javascript
import subject_filter

from File f, string mod
where
  inSubjectPath(f.getRelativePath().replaceAll("\\", "/")) and
  mod = f.getRelativePath().replaceAll("\\", "/").regexpCapture("src/([^/]+)/.*", 1)
select mod, "src/" + mod, 1, 1
