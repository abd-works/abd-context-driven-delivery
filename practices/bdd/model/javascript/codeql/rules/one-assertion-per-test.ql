/**
 * @name one-assertion-per-test
 * @practice bdd
 * @fidelity development
 * @node observation
 * @id bdd/development/one-assertion-per-test
 */

import javascript
import subject_filter
import model

from CallExpr itCall
where
  inSubject(itCall) and
  mambaIt(itCall) and
  twoAssertions(itCall.getArgument(1).(Function))
select itCall, "Example has more than one assertion.", itCall
