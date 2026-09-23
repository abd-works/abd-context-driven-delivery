import javascript
import subject_filter
import model

predicate graphRuleHit(AstNode subject, string message, AstNode contributor, string slug) {
  slug = "verb-noun-format" and
  exists(CallExpr call, string label |
    inSubject(call) and
    storyLabel(call, label) and
    subject = call and
    contributor = call and
    message = label
  )
  or
  slug = "story-name-captures-system-mechanic" and
  exists(CallExpr call, string label |
    inSubject(call) and
    storyLabel(call, label) and
    subject = call and
    contributor = call and
    message = label
  )
  or
  slug = "gwt-steps-trace-to-domain-operations" and
  exists(CallExpr call, string keyword, string label |
    inSubject(call) and
    stepCall(call, keyword) and
    label = call.getArgument(0).(StringLiteral).getValue() and
    not exists(ClassDefinition cls |
      label.toLowerCase().matches("%" + cls.getName().toLowerCase() + "%")
    ) and
    subject = call and
    contributor = call and
    message = "Step '" + label + "' does not mention a domain type from the rest of the graph."
  )
  or
  slug = "plain-english-gwt-steps" and
  exists(CallExpr call, string keyword, string label |
    inSubject(call) and
    stepCall(call, keyword) and
    label = call.getArgument(0).(StringLiteral).getValue() and
    identifierStep(label) and
    subject = call and
    contributor = call and
    message = "Step '" + label + "' is a code identifier, not a plain-English sentence."
  )
  or
  slug = "kebab-case-paths" and
  exists(File file, TopLevel top |
    kebabPath(file) and
    top.getFile() = file and
    subject = top and
    contributor = top and
    message = "Story file path is not kebab-case: " + file.getRelativePath()
  )
}
