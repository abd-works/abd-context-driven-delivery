/**
 * @name node-tier-uses-node-suffix
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node class
 * @id clean_engineering/code/node-tier-uses-node-suffix
 */

import javascript
import subject_filter
import model

from AstNode subject, string message, AstNode contributor
where
  exists(File file, TopLevel top |
    file = top.getFile() and
    inSubject(top) and
    file.getRelativePath().regexpMatch("src/[^/]+/[^/]+-server\\.ts$") and
    subject = top and
    contributor = top and
    message = "Node tier file must use <domain>-node.ts, not -server.ts."
  )
  or
  exists(ClassDefinition cls |
    inSubject(cls) and
    cls.getName().matches("%Server") and
    cls.getFile().getRelativePath().regexpMatch("src/[^/]+/[^/]+\\.(ts|tsx)$") and
    subject = cls and
    contributor = cls and
    message =
      "Node tier class " + cls.getName() +
        " must use the Node suffix (for example CustomerNode), not Server."
  )
select subject, message, contributor
