/**
 * @name public-seam-only
 * @kind problem
 * @id cdd/practice-graph/public-seam-only
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module m, string doc
where inSubject(m) and leakedInternalDoc(m) and moduleDocString(m, doc)
select m, "Module docstring leaks internals: " + doc, m
