/**
 * @name vocabulary-traces-to-domain-source
 * @practice stories
 * @fidelity
 * @node stories
 * @id stories/vocabulary-traces-to-domain-source
 * @connection clean_engineering.class
 */

import javascript
import model

from CallExpr call, string name
where untracedStory(call, name)
select call,
  "Story name '" + name +
    "' does not trace to a domain or Clean Engineering type.", call
