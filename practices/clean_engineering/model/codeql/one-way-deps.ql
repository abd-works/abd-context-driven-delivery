/**
 * @name one-way-deps
 * @kind problem
 * @id cdd/practice-graph/one-way-deps
 * @problem.severity warning
 */

import python
import subject_filter
import model

from File a, File b
where
  inSubjectPath(a.getRelativePath()) and
  cyclicModules(a, b) and
  a.getRelativePath() < b.getRelativePath()
select a,
  "File '" + a.getRelativePath() + "' and '" + b.getRelativePath() + "' depend on each other.", b
