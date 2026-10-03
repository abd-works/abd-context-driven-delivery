/**
 * @kind problem
 * @id cdd/practice-graph/test/operationLineCount
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where
  f.getName() = "huge" or
  f.getName() = "string_block" or
  f.getName() = "_write_subject_filter"
select f, f.getName() + " " + operationStatementCount(f).toString()
