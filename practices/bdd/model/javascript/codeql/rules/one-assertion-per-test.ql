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

from With block, Call itCall
where
  inSubject(block) and
  itCall = block.getContextExpr() and
  mambaIt(itCall) and
  count(Call assertion | expectCall(assertion) and assertion.getParentNode*() = block) > 1
select itCall, "Example has more than one assertion.", itCall
