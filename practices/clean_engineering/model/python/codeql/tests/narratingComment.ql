/**
 * @kind problem
 * @id cdd/practice-graph/test/narratingComment
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Comment c
where narratingComment(c)
select c, c.getText()
