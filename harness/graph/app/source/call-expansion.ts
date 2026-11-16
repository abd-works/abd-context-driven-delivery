const MAX_DEPTH = 5;

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

type ClassBody = { id: string; name: string; text: string; start: number };
type CallBody = { id: string; member: string; label: string; text: string; start: number; types: ClassBody[] };
type CallFold = { start: number; end: number; kind: "call" | "class" | "block"; member?: boolean; listed?: boolean };

export type InlineFold = { start: number; end: number; kind: "call" | "class" | "block"; glyph: number; member?: boolean; listed?: boolean };

export function initialOpenFolds(folds: InlineFold[]): number[] {
  return folds
    .filter((fold) => fold.kind === "block" && !fold.member)
    .map((fold) => fold.start);
}

export type InlineLayout = { text: string; folds: InlineFold[]; lineNumbers: string[]; depths: number[] };

export function classPanelLayout(text: string, folds: InlineFold[] = []): InlineLayout {
  const lines = text ? text.split("\n") : [""];
  return {
    text,
    folds: [...folds, ...braceFolds(text)],
    lineNumbers: lines.map((_, index) => String(index + 1)),
    depths: lines.map(() => 0),
  };
}

const STORY_CALL = /^\s*\.?(?:shareStory|story|scenario|background|given|when|then|and|but)\s*\(/;

function isStoryCall(line: string): boolean {
  return STORY_CALL.test(line) && line.includes("{");
}

function isMemberHead(line: string): boolean {
  const trimmed = line.trim();
  if (isStoryCall(trimmed)) {
    return true;
  }
  if (/^(if|for|while|switch|catch|else|try|do|return|throw)\b/.test(trimmed)) {
    return false;
  }
  if (/=>\s*\{/.test(trimmed) && !/^(public|private|protected|readonly|static|async|get|set|export)\b/.test(trimmed)) {
    return false;
  }
  return /[{]/.test(trimmed);
}

function braceFolds(text: string): InlineFold[] {
  const lines = text.split("\n");
  const folds: InlineFold[] = [];
  const classLine = /^\s*(export\s+)?(abstract\s+)?class\s+/;
  let storyContainer = false;
  for (let index = 0; index < lines.length; index += 1) {
    const container = classLine.test(lines[index]) || (isStoryCall(lines[index]) && !storyContainer);
    storyContainer = storyContainer || isStoryCall(lines[index]);
    const fold = container ? undefined : blockFoldAt(lines, index);
    if (fold) folds.push(fold);
  }
  return folds;
}

// The fold of the block that opens on the line at index, through the line that closes it; none when no block opens.
function blockFoldAt(lines: string[], index: number): InlineFold | undefined {
  if (braceDepth(lines[index]) <= 0) return undefined;
  const end = blockEnd(lines, index);
  if (end <= index) return undefined;
  return { glyph: index + 1, start: index + 2, end: end + 1, kind: "block", member: isMemberHead(lines[index]) };
}

function braceDepth(line: string): number {
  return scanBraces(line, 0).depth;
}

function blockEnd(lines: string[], start: number): number {
  let depth = 0;
  let quote = "";
  for (let line = start; line < lines.length; line += 1) {
    const scanned = scanBraces(lines[line], depth, quote);
    depth = scanned.depth;
    quote = scanned.quote;
    if (line > start && depth === 0) {
      return line;
    }
  }
  return start;
}

function scanBraces(line: string, depth: number, quote: string = ""): { depth: number; quote: string } {
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (quote) {
      if (char === "\\") {
        index += 1;
        continue;
      }
      if (char === quote) {
        quote = "";
      }
      continue;
    }
    if (char === "'" || char === '"' || char === "`") {
      quote = char;
      continue;
    }
    if (char === "{") {
      depth += 1;
    } else if (char === "}") {
      depth -= 1;
    }
  }
  return { depth, quote };
}

// Where a source's calls are laid out from: the class whose members are its own, the class it shows, and the line its
// text starts on in its file.
export type CallFocus = { owner: string; openedClass: string; origin: number };

export function inlineCallLayout(text: string, members: FoldMember[], focus: CallFocus): InlineLayout {
  const catalog = CallCatalog.of(members, focus.owner);
  const opened = focus.openedClass ? catalog.known.filter((type) => type.name === focus.openedClass).map((type) => type.id) : [];
  const layout = new CallSourceLayout(catalog, 1, opened).write(text, focus.origin || 1);
  return {
    text: layout.output.join("\n"),
    lineNumbers: layout.lineNumbers,
    depths: layout.depths,
    folds: layout.folds
      .filter((fold) => fold.end > fold.start)
      .map((fold) => ({ glyph: fold.start, start: fold.start + 1, end: fold.end, kind: fold.kind, member: fold.member, listed: fold.listed })),
  };
}

export function signatureTypeNames(text: string): string[] {
  const head = text.split("{")[0] ?? "";
  const params = head.match(/\(([^)]*)\)/)?.[1] ?? "";
  const names: string[] = [];
  for (const part of params.split(",")) {
    if (!part.includes(":")) {
      continue;
    }
    names.push(...typeIdentifiers(part.slice(part.indexOf(":") + 1)));
  }
  names.push(...returnTypeNames(head));
  return names;
}

function returnTypeNames(text: string): string[] {
  const returned = text.match(/\)\s*(?::|->)\s*([\s\S]*)$/)?.[1] ?? "";
  return typeIdentifiers(returned);
}

function fieldTypeNames(text: string): string[] {
  return typeIdentifiers(text.split(":").slice(1).join(":"));
}

function typeIdentifiers(text: string): string[] {
  return text.match(/[A-Za-z_][A-Za-z0-9_]*/g) ?? [];
}

// The declarations that give a variable its class: a typed declaration, a construction, and a typed parameter.
const VARIABLE_TYPINGS = [
  /\b(?:let|const|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^;=]+)/g,
  /\b(?:let|const|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*new\s+([A-Za-z_][A-Za-z0-9_]*)/g,
  /(?:\(|,)\s*(?:(?:public|private|protected|readonly)\s+)*([A-Za-z_][A-Za-z0-9_]*)\s*\??\s*:\s*([^,)=]+)/g,
];

function variableTypes(text: string): Map<string, string> {
  const bindings = new Map<string, string>();
  const code = withoutStrings(text).replace(/\/\/.*$/gm, " ");
  for (const typing of VARIABLE_TYPINGS) {
    for (const match of code.matchAll(typing)) {
      const typeName = typeIdentifiers(match[2]).find((name) => !SKIP_TYPES.has(name) && /^[A-Z]/.test(name));
      if (match[1] && !SKIP_TYPES.has(match[1]) && typeName) bindings.set(match[1], typeName);
    }
  }
  return bindings;
}

function withoutStrings(line: string): string {
  return line.replace(/'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`/g, " ");
}

function memberKey(owner: string, name: string): string {
  return owner ? `${owner}.${name}` : name;
}

function typesIn(kind: string, text: string, classes: Map<string, ClassBody>): ClassBody[] {
  const wanted = kind === "Property" ? fieldTypeNames(text) : signatureTypeNames(text);
  const types: ClassBody[] = [];
  const seen = new Set<string>();
  for (const name of wanted) {
    if (SKIP_TYPES.has(name) || seen.has(name)) {
      continue;
    }
    const match = classes.get(name);
    if (!match) {
      continue;
    }
    seen.add(name);
    types.push(match);
  }
  return types;
}

// Every call body and class a source's calls can list: each operation and property by its owner and name, and by its
// name alone, the shown class's own first; and each class by name. A nested listing holds the classes the line that
// opened it lists (hold), and every listing of one source shares the classes listed once already.
class CallCatalog {
  constructor(
    readonly bodies: Map<string, CallBody>,
    readonly classes: Map<string, ClassBody>,
    readonly hold: Set<string> = new Set(),
    readonly listedClasses: Set<string> = new Set(),
  ) {}

  static of(members: FoldMember[], owner: string): CallCatalog {
    const classes = new Map<string, ClassBody>();
    for (const member of members) {
      if (CLASS_KINDS.has(member.type) && member.text && !classes.has(member.name)) {
        classes.set(member.name, { id: member.node_id, name: member.name, text: member.text, start: member.start_line || 1 });
      }
    }
    const bodies = new Map<string, CallBody>();
    for (const member of ownersFirst(members, owner)) {
      const body = callBody(member, classes);
      if (!body) continue;
      if (!bodies.has(memberKey(member.owner, member.name))) bodies.set(memberKey(member.owner, member.name), body);
      if (!bodies.has(member.name)) bodies.set(member.name, body);
    }
    return new CallCatalog(bodies, classes);
  }

  get known(): ClassBody[] {
    return [...this.classes.values()];
  }

  holding(hold: Set<string>): CallCatalog {
    return new CallCatalog(this.bodies, this.classes, hold, this.listedClasses);
  }

  // The body a call of method on receiver reaches: the one of the receiver's class when a variable names it, the one of
  // a class named like the receiver, else the method of that name.
  resolve(receiver: string, method: string, typeName?: string): CallBody | undefined {
    const typed = typeName ? this.bodies.get(`${typeName}.${method}`) : undefined;
    if (typed) return typed;
    if (receiver !== "this") {
      const named = this.bodies.get(`${receiver}.${method}`) ?? this.onClassNamedLike(receiver, method);
      if (named) return named;
    }
    return this.bodies.get(method);
  }

  private onClassNamedLike(receiver: string, method: string): CallBody | undefined {
    const wanted = receiver.toLowerCase();
    for (const [key, body] of this.bodies) {
      const dot = key.lastIndexOf(".");
      if (dot >= 0 && key.slice(dot + 1) === method && key.slice(0, dot).toLowerCase() === wanted) return body;
    }
    return undefined;
  }
}

function ownersFirst(members: FoldMember[], owner: string): FoldMember[] {
  return [...members].sort((left, right) => (left.owner === owner ? 0 : 1) - (right.owner === owner ? 0 : 1));
}

// The body a call of member lists: its text and the classes its signature names; none for a member that is no call.
function callBody(member: FoldMember, classes: Map<string, ClassBody>): CallBody | undefined {
  if ((member.type !== "Operation" && member.type !== "Property") || !member.text || isSimpleProperty(member.text)) return undefined;
  return {
    id: member.node_id,
    member: member.name,
    label: member.owner ? `${member.owner}.${member.name}` : member.name,
    text: member.text,
    start: member.start_line || 1,
    types: typesIn(member.type, member.text, classes),
  };
}

// One block a line opens: the line it opens on, the brace depth it opened to, and whether it is a member's body.
type OpenBlock = { at: number; openedTo: number; member: boolean };

const CLASS_DECLARATION = /^\s*(export\s+)?(abstract\s+)?class\s+/;

// A source laid out with the body of each call it makes listed under the call's line, and each class a line names under
// it, to MAX_DEPTH: the lines written, the number each has in its own file, how deep each is listed, and the folds that
// close each call, class, and block.
class CallSourceLayout {
  readonly output: string[] = [];
  readonly lineNumbers: string[] = [];
  readonly depths: number[] = [];
  readonly folds: CallFold[] = [];
  private readonly blocks: OpenBlock[] = [];
  private bindings = new Map<string, string>();
  private brace = 0;
  private quote = "";
  private storyContainer = false;

  constructor(private readonly catalog: CallCatalog, private readonly depth: number, private readonly stack: string[]) {}

  write(text: string, origin: number): CallSourceLayout {
    this.bindings = variableTypes(text);
    text.split("\n").forEach((line, index) => {
      this.push(line, String(origin + index), Math.max(0, this.depth - 1));
      this.openBlocks(line);
      if (this.depth < MAX_DEPTH) this.listUnder(line);
      this.closeBlocks();
    });
    return this;
  }

  private push(line: string, number: string, depth: number): void {
    this.output.push(line);
    this.lineNumbers.push(number);
    this.depths.push(depth);
  }

  private openBlocks(line: string): void {
    const at = this.output.length;
    const before = this.brace;
    const scanned = scanBraces(line, this.brace, this.quote);
    this.brace = scanned.depth;
    this.quote = scanned.quote;
    const openingStory = isStoryCall(line) && !this.storyContainer;
    this.storyContainer = this.storyContainer || isStoryCall(line);
    if (CLASS_DECLARATION.test(line) || openingStory) return;
    const member = isMemberHead(line);
    for (let next = before + 1; next <= this.brace; next += 1) {
      this.blocks.push({ at, openedTo: next, member: member && next === before + 1 });
    }
  }

  // List under line each call it makes and each class it names, and fold them under it.
  private listUnder(line: string): void {
    const calls = this.callsOnLine(line);
    const constructed = typesConstructed(line, this.catalog.known);
    const listedTypes = this.typesListed(line, calls, constructed);
    const pad = `${indentOf(line)}    `;
    const callLine = this.output.length;
    const held = new Set(listedTypes.map((type) => type.id));
    for (const call of calls) this.appendOperation(call, pad, held);
    for (const type of listedTypes) this.appendClass(type, pad, constructed.some((item) => item.id === type.id));
    if ((calls.length > 0 || listedTypes.length > 0) && this.output.length > callLine) {
      this.folds.push({ start: callLine, end: this.output.length, kind: calls.length > 0 ? "call" : "class", listed: calls.length === 0 });
    }
  }

  // The classes listed under line: those its calls take, those it names or holds in a variable, and those it
  // constructs, each once, none the nesting holds unless the line constructs it.
  private typesListed(line: string, calls: CallBody[], constructed: ClassBody[]): ClassBody[] {
    const fromCalls = typesOn(calls);
    const mentioned: ClassBody[] = [];
    const named = [...this.catalog.known.filter((type) => mentionsType(line, type.name)), ...typesForVariables(line, this.bindings, this.catalog.known)];
    for (const type of named) {
      const listed = this.stack.includes(type.id) || [...fromCalls, ...mentioned].some((item) => item.id === type.id);
      if (!listed) mentioned.push(type);
    }
    return [...fromCalls, ...mentioned, ...constructed].filter(
      (type, typeIndex, all) =>
        all.findIndex((other) => other.id === type.id) === typeIndex &&
        (!this.catalog.hold.has(type.id) || constructed.some((other) => other.id === type.id)),
    );
  }

  private callsOnLine(line: string): CallBody[] {
    const found: CallBody[] = [];
    const pattern = /\b([A-Za-z_][A-Za-z0-9_]*)\??\.([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
    let match: RegExpExecArray | null;
    while ((match = pattern.exec(line))) {
      const body = SKIP_TYPES.has(match[1]) ? undefined : this.catalog.resolve(match[1], match[2], this.bindings.get(match[1]));
      if (body && !this.stack.includes(body.id) && !found.some((listed) => listed.id === body.id) && !isSimpleProperty(body.text)) found.push(body);
      const next = match.index + match[1].length + (match[0].includes("?.") ? 2 : 1);
      if (pattern.lastIndex > next) pattern.lastIndex = next;
    }
    return found;
  }

  private appendOperation(call: CallBody, pad: string, hold: Set<string>): void {
    this.push(`${pad}${call.member}`, String(call.start || ""), this.depth);
    const operationLine = this.output.length;
    const nested = new CallSourceLayout(this.catalog.holding(hold), this.depth + 1, [...this.stack, call.id]).write(call.text, call.start || 1);
    this.appendNested(nested, `${pad}    `);
    if (this.output.length > operationLine) this.folds.push({ start: operationLine, end: this.output.length, kind: "call" });
    for (const fold of nested.folds) {
      if (fold.start === 1 && fold.kind === "block") continue;
      this.folds.push({ start: operationLine + fold.start, end: operationLine + fold.end, kind: fold.kind, member: fold.member, listed: fold.listed });
    }
  }

  private appendNested(nested: CallSourceLayout, bodyPad: string): void {
    nested.output.forEach((nestedLine, index) => {
      this.push(nestedLine.length > 0 ? `${bodyPad}${nestedLine}` : bodyPad, nested.lineNumbers[index] ?? "", (nested.depths[index] ?? this.depth) + 1);
    });
  }

  // List type's text under the line, once in the whole layout unless the line constructs it again.
  private appendClass(type: ClassBody, pad: string, again: boolean): void {
    const listed = this.catalog.listedClasses;
    if (this.stack.includes(type.id) || (listed.has(type.id) && !again)) return;
    listed.add(type.id);
    this.push(`${pad}${type.name}`, String(type.start || ""), this.depth);
    const classLine = this.output.length;
    const classLines = type.text.split("\n");
    if (classLines.length === 0 || (classLines.length === 1 && classLines[0].trim() === type.name)) return;
    classLines.forEach((classLineText, index) => {
      this.push(classLineText.length > 0 ? `${pad}    ${classLineText}` : `${pad}    `, String((type.start || 1) + index), this.depth + 1);
    });
    this.folds.push({ start: classLine, end: this.output.length, kind: "class", listed: true });
    for (const brace of braceFolds(type.text)) {
      this.folds.push({ start: classLine + brace.glyph, end: classLine + brace.end, kind: "block", member: brace.member });
    }
  }

  // Fold each block the brace depth has closed, but one whose opening line already folds a listing.
  private closeBlocks(): void {
    while (this.blocks.length > 0 && this.brace < this.blocks[this.blocks.length - 1].openedTo) {
      const block = this.blocks.pop();
      if (!block || this.output.length <= block.at) continue;
      if (this.folds.some((fold) => fold.start === block.at && (fold.kind === "call" || fold.kind === "class"))) continue;
      this.folds.push({ start: block.at, end: this.output.length, kind: "block", member: block.member });
    }
  }
}

function isSimpleProperty(text: string): boolean {
  const lines = text.split("\n").map((line) => line.trim()).filter((line) => line.length > 0);
  if (lines.length !== 1) {
    return false;
  }
  const line = lines[0];
  if (/^(?:public\s+|private\s+|protected\s+|readonly\s+|static\s+|abstract\s+|override\s+|declare\s+)*(?:get|set)\s+[A-Za-z_]/.test(line) && line.includes("{") && line.includes("}")) {
    return true;
  }
  return !line.includes("(") && /[:=]/.test(line);
}

function wordHas(line: string, name: string): boolean {
  return new RegExp(`\\b${name}\\b`).test(line);
}

function typesForVariables(line: string, bindings: Map<string, string>, known: ClassBody[]): ClassBody[] {
  const code = withoutStrings(line);
  const found: ClassBody[] = [];
  for (const [variable, typeName] of bindings) {
    const type = wordHas(code, variable) ? known.find((item) => item.name === typeName) : undefined;
    if (type && !found.some((item) => item.id === type.id) && !SKIP_TYPES.has(type.name)) found.push(type);
  }
  return found;
}

function typesConstructed(line: string, known: ClassBody[]): ClassBody[] {
  const found: ClassBody[] = [];
  for (const match of withoutStrings(line).matchAll(/\bnew\s+([A-Za-z_][A-Za-z0-9_]*)\b/g)) {
    const type = known.find((item) => item.name === match[1]);
    if (type && !found.some((item) => item.id === type.id) && !SKIP_TYPES.has(type.name)) found.push(type);
  }
  return found;
}

function mentionsType(line: string, name: string): boolean {
  return !SKIP_TYPES.has(name) && wordHas(withoutStrings(line), name);
}

function typesOn(calls: CallBody[]): ClassBody[] {
  const types: ClassBody[] = [];
  for (const type of calls.flatMap((call) => call.types)) {
    if (!types.some((listed) => listed.id === type.id)) types.push(type);
  }
  return types;
}

function indentOf(line: string): string {
  return line.match(/^\s*/)?.[0] ?? "";
}
