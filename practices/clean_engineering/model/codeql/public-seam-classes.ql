/**
 * @kind problem
 * @id cdd/practice-graph/verify/public-seam-classes
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class cls, string prefix
where
  inSource(cls) and
  not skippedModulePath(normalizedPath(cls.getLocation().getFile())) and
  prefix = enclosingFirstClassPrefix(normalizedPath(cls.getLocation().getFile())) and
  publicName(cls.getName())
select prefix, cls.getName()
