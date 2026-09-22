/**
 * @name Practice graph classes
 * @kind problem
 * @id cdd/practice-graph/classes
 */

import python
import subject_filter

from Class cls
where inSubject(cls)
select cls.getName(), cls.getEnclosingModule().getName(),
  cls.getLocation().getFile().getRelativePath(), cls.getLocation().getStartLine()
