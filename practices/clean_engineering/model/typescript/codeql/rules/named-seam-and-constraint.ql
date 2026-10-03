/**
 * @name named-seam-and-constraint
 * @practice clean_engineering
 * @fidelity modules
 * @node module
 * @id clean_engineering/modules/named-seam-and-constraint
 */

import javascript
import subject_filter
import model

from Module m, string doc
where inSubject(m) and missingSeamOrConstraint(m) and moduleDocString(m, doc)
select m, "Module docstring does not name both seam and constraint: " + doc, m
