/**
 * @name originating-sub-epic-examples
 * @kind problem
 * @id paradise/originating-sub-epic-examples
 * @problem.severity warning
 */

import javascript

from File example
where
  example
      .getRelativePath()
      .regexpMatch("(?i).*tests/[^/]+/examples/.*\\.examples\\.ts")
select example,
  "Example file '" + example.getBaseName() +
    "' sits in the epic examples folder. Place it in the examples folder of the sub-epic whose story originates the fixture.",
  example
