/**
 * @name constants-not-magic-strings
 * @kind problem
 * @id paradise/constants-not-magic-strings
 * @problem.severity warning
 */

import javascript

from EqualityTest test, StringLiteral literal
where
  literal = test.getAnOperand() and
  literal.getValue() = ["eSIM", "pSIM", "rate_limited", "invalid_number"]
select literal,
  "Magic string '" + literal.getValue() +
    "' belongs on a named const such as SimType or PortabilityStatus.",
  literal
