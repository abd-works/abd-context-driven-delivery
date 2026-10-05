import python
import model

bindingset[hint]
predicate isRelativeHint(string hint) {
  hint.regexpMatch(".*[A-Z][A-Za-z0-9_].*") and
  not hint.regexpMatch(".*(Repository|Requirements|Operation|Exception|Error).*")
}
