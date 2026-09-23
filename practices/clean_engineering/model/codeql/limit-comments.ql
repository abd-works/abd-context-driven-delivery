/**
 * @name limit-comments
 * @kind problem
 * @id cdd/practice-graph/limit-comments
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Comment c
where
  inSubjectPath(c.getLocation().getFile().getRelativePath()) and
  narratingComment(c)
select c, "Comment narrates code instead of stating a constraint: '" + c.getText() + "'.", c
