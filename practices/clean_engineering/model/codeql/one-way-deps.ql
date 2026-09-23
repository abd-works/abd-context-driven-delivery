/**
 * @name one-way-deps
 * @kind problem
 * @id cdd/practice-graph/one-way-deps
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module a, Module b
where
  inSubjectPath(a.getFile().getRelativePath()) and
  cyclicModules(a, b) and
  a.getFile().getRelativePath() < b.getFile().getRelativePath()
select a,
  "Module '" + a.getName() + "' and '" + b.getName() + "' depend on each other.", b
