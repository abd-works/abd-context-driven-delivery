/**
 * @name vocabulary-traces-to-domain-source
 * @kind problem
 * @id cdd/practice-graph/vocabulary-traces-to-domain-source
 * @problem.severity warning
 */

import python
import model

from Call call, string name
where untracedStory(call, name)
select call,
  "Story name '" + name +
    "' does not trace to a domain or Clean Engineering type.", call
