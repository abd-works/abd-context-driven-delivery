/**
 * @name ask-cross-aggregate-sync
 * @practice stories
 * @pattern lern_domain_driven
 * @fidelity acceptance_tests
 * @node module
 * @id stories/acceptance_tests/ask-cross-aggregate-sync
 * @connection ddd.tactics
 */

import javascript
import subject_filter
import model

from Container a, Container b, File f, TopLevel top, string message, AstNode contributor
where
  domainFolder(a) and
  domainFolder(b) and
  a.getRelativePath() < b.getRelativePath() and
  not exists(StringLiteral s |
    s.getValue().toLowerCase().matches("%event-based%") or
    s.getValue().toLowerCase().matches("%single-aggregate%") or
    s.getValue().toLowerCase().matches("%direct repository%")
  ) and
  f.getParentContainer() = a and
  top.getFile() = f and
  inSubject(top) and
  message =
    "This slice has more than one aggregate. AskQuestion for cross-aggregate sync before generating stories." and
  contributor = top
select top, message, contributor
