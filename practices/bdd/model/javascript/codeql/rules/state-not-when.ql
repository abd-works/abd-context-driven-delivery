/**
 * @name state-not-when
 * @practice bdd
 * @fidelity
 * @node describe
 * @id bdd/state-not-when
 */

import javascript
import subject_filter
import model

from CallExpr call
where inSubject(call) and whenContext(call)
select call, "Nested state is named with 'when' instead of a condition.", call
