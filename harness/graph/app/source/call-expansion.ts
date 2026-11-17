import type { SourceCallout } from "./source-callouts";

const SKIP_TYPES = new Set([
  "string",
  "number",
  "boolean",
  "unknown",
  "void",
  "any",
  "null",
  "undefined",
  "object",
  "never",
  "bigint",
  "symbol",
  "str",
  "int",
  "float",
  "bool",
  "None",
  "list",
  "dict",
  "self",
  "Promise",
  "Array",
  "Readonly",
  "Partial",
  "Record",
  "Map",
  "Set",
  "Date",
  "console",
  "Math",
  "JSON",
  "Object",
  "expect",
]);

const CLASS_KINDS = new Set([
  "OoadClass",
  "Entity",
  "EntityRoot",
  "ValueObject",
  "Aggregate",
  "Repository",
  "DomainEvent",
  "DomainService",
  "Specification",
]);

// The marker the graph puts after a line for each call on it, `/* call:isinstance */`, which is no code and never shows.
const CALL_MARKER = /[ \t]*\/\* call:[^*]*\*\//g;
const MEMBER_CALL = /\b([A-Za-z_][A-Za-z0-9_]*)\??\.([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
// A call by a bare name, `reread_all(board)`, which a module's own function answers; never a member call, `a.b(`.
const BARE_CALL = /(?<![\w.$])([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
// The receivers that name the object a method runs on: a call on them opens a member of the class around the line.
const OWN_OBJECT = new Set(["self", "this"]);
const QUOTED = /'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`/g;

// A class, operation or property the session's graph holds, with its text, from which a callout opens it in place.
export type FoldMember = {
  node_id: string;
  name: string;
  type: string;
  owner: string;
  text: string;
  file: string;
  start_line: number;
  end_line: number;
  classes?: string[];
};

type Body = { id: string; name: string; label: string; text: string; file: string; start: number; end: number; owner: string };

// The members of a graph a source view opens calls and classes from: each class by its name, each operation and property
// by its class and name. calloutsIn finds, line by line, the calls and classes the code of a text reaches; a name in a
// comment, a docstring or a string is prose, which opens nothing.
export class CallCatalog {
  private readonly classes = new Map<string, Body>();
  private readonly bodies = new Map<string, Body>();
  // The module functions a call by a bare name opens, by name.
  private readonly functions = new Map<string, Body>();
  // Every class and every member the graph holds, however many files define one of the same name, so the open file's
  // own answers a name before another file's.
  private readonly everyClass: Body[] = [];
  private readonly everyMember: Body[] = [];

  constructor(members: FoldMember[], owner = "") {
    for (const member of members) this.hold(member, owner);
  }

  // The callouts of each line of text, which starts at file line origin of file: each call, then each class the line
  // names in code, a class once per text. stack holds the members already open around it, which never open again
  // inside, and no line opens a class or member whose own lines of file hold it: a definition never opens itself.
  calloutsIn(text: string, origin: number, language: string, stack: string[] = [], file = ""): SourceCallout[] {
    const code = codeOf(text, language).split("\n");
    const bindings = variableTypes(code.join("\n"));
    const seen = new Set<string>(stack);
    return code.flatMap((line, index) => this.calloutsOn(line, { file, line: origin + index }, bindings, stack, seen));
  }

  private calloutsOn(line: string, at: FileLine, bindings: Map<string, string>, stack: string[], seen: Set<string>): SourceCallout[] {
    const outside = (body: Body) => !holds(body, at);
    const calls = this.callsOn(line, bindings, at).filter((call) => !stack.includes(call.id) && outside(call));
    const types = [...this.classes.values()].map((type) => this.classNamed(type.name, at)).filter((type) => !seen.has(type.id) && outside(type) && (namesType(line, type.name) || boundOn(line, bindings, type.name)));
    types.forEach((type) => seen.add(type.id));
    return [...calls.map((call) => calloutOf(call, at.line, "call")), ...types.map((type) => calloutOf(type, at.line, "class"))];
  }

  private callsOn(line: string, bindings: Map<string, string>, at: FileLine): Body[] {
    const found: Body[] = [];
    const add = (body: Body | undefined) => {
      if (body && !found.includes(body)) found.push(body);
    };
    for (const match of line.matchAll(MEMBER_CALL)) {
      if (OWN_OBJECT.has(match[1])) add(this.ownMember(match[2], at));
      else add(SKIP_TYPES.has(match[1]) ? undefined : this.resolve(match[1], match[2], bindings.get(match[1])));
    }
    for (const match of line.matchAll(BARE_CALL)) add(this.functions.get(match[1]));
    return found;
  }

  // The member called method of the class whose lines of the file hold the call, as `self.close()` calls it.
  private ownMember(method: string, at: FileLine): Body | undefined {
    const around = this.everyClass.find((type) => holds(type, at));
    if (!around) return undefined;
    const named = this.everyMember.filter((member) => member.owner === around.name && member.name === method);
    return named.find((member) => sameFile(member.file, around.file)) ?? named[0];
  }

  // The class called name that a line of the open file means: the open file's own when it defines one, else the
  // first the graph holds.
  private classNamed(name: string, at: FileLine): Body {
    const own = this.everyClass.find((type) => type.name === name && sameFile(type.file, at.file));
    return own ?? (this.classes.get(name) as Body);
  }

  private resolve(receiver: string, method: string, typeName?: string): Body | undefined {
    const typed = typeName ? this.bodies.get(`${typeName}.${method}`) : undefined;
    if (typed) return typed;
    const exact = receiver === "this" ? undefined : this.bodies.get(`${receiver}.${method}`);
    if (exact) return exact;
    const byReceiver = [...this.bodies.entries()].find(([key]) => key.toLowerCase() === `${receiver}.${method}`.toLowerCase());
    return byReceiver?.[1] ?? this.bodies.get(method);
  }

  private hold(member: FoldMember, owner: string): void {
    if (!member.text) return;
    const body = bodyOf(member);
    if (CLASS_KINDS.has(member.type)) {
      this.everyClass.push(body);
      if (!this.classes.has(member.name)) this.classes.set(member.name, body);
      return;
    }
    if (member.type === "Operation" || member.type === "Property") this.everyMember.push(body);
    if ((member.type !== "Operation" && member.type !== "Property") || isSimpleProperty(member.text)) return;
    const key = member.owner ? `${member.owner}.${member.name}` : member.name;
    if (isModuleFunction(member) && !this.functions.has(member.name)) this.functions.set(member.name, body);
    // A member of the class the text belongs to answers a bare name before any other class's.
    if (!this.bodies.has(key)) this.bodies.set(key, body);
    if (!this.bodies.has(member.name) || member.owner === owner) this.bodies.set(member.name, body);
  }
}

// The text without the marker the graph puts after a line for each call on it, which is no code.
export function withoutCallMarkers(text: string): string {
  return text.replace(CALL_MARKER, "");
}

function bodyOf(member: FoldMember): Body {
  const text = withoutCallMarkers(member.text);
  const start = member.start_line || 1;
  const label = member.owner && !isModuleFunction(member) ? `${member.owner}.${member.name}` : member.name;
  return { id: member.node_id, name: member.name, label, text, file: member.file, start, end: member.end_line || start + text.split("\n").length - 1, owner: member.owner };
}

// The owner the graph gives a module's own function (Clean Engineering's MODULE_FUNCTION_HOLDER), which no class is.
export const MODULE_OWNER = "_module";

// Whether member is a function of its module, not of a class: owned by the module, or by nothing.
function isModuleFunction(member: FoldMember): boolean {
  return member.type === "Operation" && (!member.owner || member.owner === MODULE_OWNER);
}

// A line of a file, from 1, which a callout is found on.
type FileLine = { file: string; line: number };

// Whether body's own lines of its file hold the line at: its definition, and every line inside it.
function holds(body: Body, at: FileLine): boolean {
  return sameFile(body.file, at.file) && body.start <= at.line && at.line <= body.end;
}

// Whether two names of a file name the same file: one may be named from the project and the other from its practice's
// root below it, as harness/diagnostics/app.py and diagnostics/app.py are.
function sameFile(one: string, other: string): boolean {
  if (!one || !other) return false;
  const [shorter, longer] = one.length <= other.length ? [one, other] : [other, one];
  return longer === shorter || longer.endsWith(`/${shorter}`);
}

function calloutOf(body: Body, line: number, kind: SourceCallout["kind"]): SourceCallout {
  return { id: body.id, kind, line, title: body.label, path: body.file, startLine: body.start, endLine: body.end, text: body.text };
}

// The text with every comment, docstring and string blanked out, its lines kept, so only code is searched for names.
export function codeOf(text: string, language: string): string {
  const hashComments = language === "python";
  let out = "";
  let index = 0;
  while (index < text.length) {
    const skipped = proseAt(text, index, hashComments);
    out += skipped > index ? text.slice(index, skipped).replace(/[^\n]/g, " ") : text[index];
    index = Math.max(skipped, index + 1);
  }
  return out;
}

// Where the comment or string starting at index ends; index itself when none starts there.
function proseAt(text: string, index: number, hashComments: boolean): number {
  const rest = text.slice(index, index + 3);
  const closing = rest === '"""' || rest === "'''" ? rest : rest.startsWith("/*") ? "*/" : "";
  if (closing) return endOf(text, text.indexOf(closing, index + 2), closing.length);
  if (rest.startsWith("//") || (hashComments && rest.startsWith("#"))) return endOf(text, text.indexOf("\n", index), 0);
  const quote = text[index];
  if (quote !== "'" && quote !== '"' && quote !== "`") return index;
  let at = index + 1;
  while (at < text.length && text[at] !== quote && (quote === "`" || text[at] !== "\n")) at += text[at] === "\\" ? 2 : 1;
  return Math.min(at + 1, text.length);
}

function endOf(text: string, found: number, length: number): number {
  return found < 0 ? text.length : found + length;
}

function namesType(line: string, name: string): boolean {
  return !SKIP_TYPES.has(name) && new RegExp(`\\b${name}\\b`).test(line);
}

function boundOn(line: string, bindings: Map<string, string>, typeName: string): boolean {
  return [...bindings].some(([variable, bound]) => bound === typeName && new RegExp(`\\b${variable}\\b`).test(line));
}

function isSimpleProperty(text: string): boolean {
  const lines = text.split("\n").map((line) => line.trim()).filter((line) => line.length > 0);
  if (lines.length !== 1) return false;
  const line = lines[0];
  if (/^(?:public\s+|private\s+|protected\s+|readonly\s+|static\s+|abstract\s+|override\s+|declare\s+)*(?:get|set)\s+[A-Za-z_]/.test(line) && line.includes("{") && line.includes("}")) return true;
  return !line.includes("(") && /[:=]/.test(line);
}

// The class each variable of the code is declared as, so a call on it opens that class's member.
function variableTypes(code: string): Map<string, string> {
  const bindings = new Map<string, string>();
  const bind = (name: string, typeText: string) => {
    const typeName = (typeText.match(/[A-Za-z_][A-Za-z0-9_]*/g) ?? []).find((item) => !SKIP_TYPES.has(item) && /^[A-Z]/.test(item));
    if (name && !SKIP_TYPES.has(name) && typeName) bindings.set(name, typeName);
  };
  const plain = code.replace(QUOTED, " ");
  for (const match of plain.matchAll(/\b(?:let|const|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^;=]+)/g)) bind(match[1], match[2]);
  for (const match of plain.matchAll(/\b(?:let|const|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*new\s+([A-Za-z_][A-Za-z0-9_]*)/g)) bind(match[1], match[2]);
  for (const match of plain.matchAll(/(?:\(|,)\s*(?:(?:public|private|protected|readonly)\s+)*([A-Za-z_][A-Za-z0-9_]*)\s*\??\s*:\s*([^,)=]+)/g)) bind(match[1], match[2]);
  return bindings;
}
