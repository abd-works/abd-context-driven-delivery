/**
 * @name named-seam-and-constraint
 * @kind problem
 * @id cdd/practice-graph/named-seam-and-constraint
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module m, string doc
where inSubject(m) and missingSeamOrConstraint(m) and moduleDocString(m, doc)
select m, "Module docstring does not name both seam and constraint: " + doc, m
