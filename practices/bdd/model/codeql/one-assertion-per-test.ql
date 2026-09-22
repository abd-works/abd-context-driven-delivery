/**
 * @name one-assertion-per-test
 * @kind problem
 * @id cdd/practice-graph/one-assertion-per-test
 * @problem.severity warning
 */

import python
import subject_filter
import model

from With block, Call itCall
where
  inSubject(block) and
  itCall = block.getContextExpr() and
  mambaIt(itCall) and
  count(Call assertion | expectCall(assertion) and assertion.getParentNode*() = block) > 1
select itCall, "Example has more than one assertion.", itCall
