/**
 * @name ask-cross-aggregate-sync
 * @practice ddd
 * @pattern lern_domain_driven
 * @fidelity building_blocks
 * @node module
 * @id ddd/building_blocks/ask-cross-aggregate-sync
 */

import javascript
import subject_filter
import model

from Container a, Container b, File f, TopLevel top, string message, AstNode contributor
where
  domainFolder(a) and
  domainFolder(b) and
  a.getParentContainer() = b.getParentContainer() and
  a.getRelativePath() < b.getRelativePath() and
  not exists(File note |
    note.getParentContainer() = a.getParentContainer() and
    note.getBaseName().toLowerCase().matches("%sync%")
  ) and
  f.getParentContainer() = a and
  top.getFile() = f and
  inSubject(top) and
  message =
    "This slice has more than one aggregate. AskQuestion for cross-aggregate sync before generating stories." and
  contributor = top
select top, message, contributor
