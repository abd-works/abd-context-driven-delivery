/**
 * @name observable-behavior
 * @practice bdd
 * @fidelity
 * @node observation
 * @id bdd/observable-behavior
 */

import javascript
import subject_filter
import model

from CallExpr call
where inSubject(call) and observesPrivate(call)
select call, "Assertion observes a private attribute instead of stakeholder-visible behaviour.", call
