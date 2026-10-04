import javascript

predicate storyFile(File file) {
  file
      .getBaseName()
      .regexpMatch(".*(_story\\.(test|spec)|\\.story\\.(shared|domain\\.spec|server\\.spec|playwright))\\.[jt]sx?$")
}

predicate storyCall(CallExpr call) {
  storyFile(call.getFile()) and
  call.getCalleeName() = ["story", "shareStory"]
}

predicate stepCall(CallExpr call) {
  storyFile(call.getFile()) and
  call.getCalleeName() = ["given", "when", "then", "and", "but"]
}

string storyTitle(CallExpr call) {
  exists(CallExpr story |
    storyCall(story) and
    call.getParent*() = story and
    result = story.getArgument(0).(StringLiteral).getValue()
  )
}

string scenarioTitle(CallExpr call) {
  exists(CallExpr scenario |
    scenario.getCalleeName() = "scenario" and
    scenario.getArgument(0) instanceof StringLiteral and
    call.getParent*() = scenario and
    result = scenario.getArgument(0).(StringLiteral).getValue()
  )
}

string backgroundTitle(CallExpr call) {
  exists(CallExpr background, string raw |
    background.getCalleeName() = "background" and
    call.getParent*() = background and
    raw = background.getArgument(0).(StringLiteral).getValue() and
    (
      if raw = "each" or raw = "all" or raw = ""
      then result = "background"
      else result = raw
    )
  )
}

string typeName(TypeExpr type) {
  result = type.(LocalTypeAccess).getName()
  or
  result = typeName(type.(GenericTypeExpr).getATypeArgument())
  or
  result = typeName(type.(UnionTypeExpr).getAnElementType())
  or
  result = typeName(type.(ParenthesizedTypeExpr).getElementType())
  or
  result = typeName(type.(ArrayTypeExpr).getElementType())
}

string receiverClass(Expr receiver) {
  result =
    typeName(receiver.(VarAccess).getVariable().getADeclaration().(VarDecl).getTypeAnnotation())
}

/** Line of the step text. A chained .and() starts at the receiver, so the call line is the given. */
int stepLine(CallExpr call) {
  result = call.getArgument(0).(StringLiteral).getLocation().getStartLine()
  or
  not exists(call.getArgument(0).(StringLiteral)) and result = call.getLocation().getStartLine()
}
