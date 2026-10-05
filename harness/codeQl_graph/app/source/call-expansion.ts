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

export type FoldNode = {
  nodeId: string;
  name: string;
  nodeType?: { name?: string } | null;
  source?: { text?: string; file?: string; startLine?: number; endLine?: number } | null;
  children?: FoldNode[];
};

export type FoldMember = {
  id: string;
  name: string;
  kind: string;
  owner: string;
  text: string;
  file: string;
  start: number;
  end: number;
  classes?: string[];
};

type ClassBody = { id: string; name: string; text: string };
type CallBody = { id: string; member: string; label: string; text: string; types: ClassBody[] };
type CallFold = { start: number; end: number; kind: "call" | "class" | "block"; member?: boolean; listed?: boolean };

export type InlineFold = { start: number; end: number; kind: "call" | "class" | "block"; glyph: number; member?: boolean; listed?: boolean };

export function initialOpenFolds(folds: InlineFold[]): number[] {
  return folds
    .filter((fold) => fold.kind === "block" && !fold.member)
    .map((fold) => fold.start);
}

export type InlineLayout = { text: string; folds: InlineFold[]; lineNumbers: string[]; depths: number[] };

export function collectFoldMembers(nodes: FoldNode[]): FoldMember[] {
  const seen = new Map<string, FoldMember>();
  const visit = (node: FoldNode, owner: string, parentIsClass: boolean) => {
    const kind = node.nodeType?.name ?? "";
    const isClass = CLASS_KINDS.has(kind);
    const grouped = kind === "FieldGroup";
    if ((kind === "Operation" || kind === "Property" || isClass) && node.nodeId) {
      const existing = seen.get(node.nodeId);
      const realOwner = isClass ? "" : parentIsClass ? owner : (existing?.owner ?? "");
      if (!existing) {
        seen.set(node.nodeId, {
          id: node.nodeId,
          name: node.name,
          kind,
          owner: realOwner,
          text: node.source?.text ?? "",
          file: node.source?.file ?? "",
          start: Number(node.source?.startLine) || 0,
          end: Number(node.source?.endLine) || 0,
        });
      } else {
        if (parentIsClass && !isClass) {
          existing.owner = owner;
        }
        if (!existing.text && node.source?.text) {
          existing.text = node.source.text;
        }
        if (!existing.file && node.source?.file) {
          existing.file = node.source.file;
          existing.start = Number(node.source.startLine) || existing.start;
          existing.end = Number(node.source.endLine) || existing.end;
        }
      }
    }
    const nextOwner = isClass ? node.name : owner;
    for (const child of node.children ?? []) {
      visit(child, nextOwner, isClass || (grouped && parentIsClass));
    }
  };
  for (const node of nodes) {
    visit(node, "", false);
  }
  return [...seen.values()];
}

export function classPanelLayout(text: string, folds: InlineFold[] = []): InlineLayout {
  const lines = text ? text.split("\n") : [""];
  return {
    text,
    folds: [...folds, ...braceFolds(text)],
    lineNumbers: lines.map((_, index) => String(index + 1)),
    depths: lines.map(() => 0),
  };
}

function isMemberHead(line: string): boolean {
  const trimmed = line.trim();
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
  for (let index = 0; index < lines.length; index += 1) {
    if (classLine.test(lines[index]) || braceDepth(lines[index]) <= 0) {
      continue;
    }
    const end = blockEnd(lines, index);
    if (end <= index) {
      continue;
    }
    folds.push({
      glyph: index + 1,
      start: index + 2,
      end: end + 1,
      kind: "block",
      member: isMemberHead(lines[index]),
    });
  }
  return folds;
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

function scanBraces(line: string, depth: number, quote = ""): { depth: number; quote: string } {
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

export function inlineCallLayout(
  text: string,
  members: FoldMember[],
  owner: string,
  options: {
    anchored?: FoldMember[];
    listClasses?: boolean;
    named?: FoldMember[];
    openedClass?: string;
    context?: string;
  } = {},
): InlineLayout {
  const classes = classCatalog(members);
  const bodies = callCatalog(members, classes, owner);
  const known = [...classes.values()];
  const bindings = variableTypes(options.context ?? "");
  const anchored = (options.anchored ?? [])
    .map((member) => bodies.get(memberKey(member.owner || owner, member.name)) ?? bodiesByMember(bodies).get(member.name))
    .filter((body): body is CallBody => Boolean(body));
  const namedCalls: CallBody[] = [];
  const namedClasses: ClassBody[] = [];
  for (const member of options.named ?? []) {
    if (CLASS_KINDS.has(member.kind)) {
      const listed = classes.get(member.name);
      if (listed && !namedClasses.some((item) => item.id === listed.id)) {
        namedClasses.push(listed);
      }
      continue;
    }
    namedCalls.push({
      id: member.id,
      member: member.name,
      label: member.name,
      text: member.text || member.name,
      types: (member.classes ?? [])
        .map((name) => classes.get(name))
        .filter((item): item is ClassBody => Boolean(item)),
    });
  }
  const opened = options.openedClass ?? "";
  const layout = displayedCallSource(
    text,
    bodies,
    1,
    opened ? known.filter((type) => type.name === opened).map((type) => type.id) : [],
    known,
    anchored,
    options.listClasses ?? false,
    namedCalls,
    namedClasses,
    new Set(),
    new Set(),
    bindings,
  );
  return {
    text: layout.text,
    lineNumbers: layout.lineNumbers,
    depths: layout.depths,
    folds: layout.folds
      .filter((fold) => fold.end > fold.start)
      .map((fold) => ({
        glyph: fold.start,
        start: fold.start + 1,
        end: fold.end,
        kind: fold.kind,
        member: fold.member,
        listed: fold.listed,
      })),
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

function variableTypes(text: string): Map<string, string> {
  const bindings = new Map<string, string>();
  const code = text
    .replace(/'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`/g, " ")
    .replace(/\/\/.*$/gm, " ");
  const bind = (name: string, typeText: string) => {
    if (!name || SKIP_TYPES.has(name)) {
      return;
    }
    const typeName = typeIdentifiers(typeText).find((item) => !SKIP_TYPES.has(item) && /^[A-Z]/.test(item));
    if (typeName) {
      bindings.set(name, typeName);
    }
  };
  for (const match of code.matchAll(/\b(?:let|const|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^;=]+)/g)) {
    bind(match[1], match[2]);
  }
  for (const match of code.matchAll(
    /\b(?:let|const|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*new\s+([A-Za-z_][A-Za-z0-9_]*)/g,
  )) {
    bind(match[1], match[2]);
  }
  for (const match of code.matchAll(
    /(?:\(|,)\s*(?:(?:public|private|protected|readonly)\s+)*([A-Za-z_][A-Za-z0-9_]*)\s*\??\s*:\s*([^,)=]+)/g,
  )) {
    bind(match[1], match[2]);
  }
  return bindings;
}

function classCatalog(members: FoldMember[]): Map<string, ClassBody> {
  const classes = new Map<string, ClassBody>();
  for (const member of members) {
    if (!CLASS_KINDS.has(member.kind) || !member.text || classes.has(member.name)) {
      continue;
    }
    classes.set(member.name, { id: member.id, name: member.name, text: member.text });
  }
  return classes;
}

function callCatalog(members: FoldMember[], classes: Map<string, ClassBody>, owner: string): Map<string, CallBody> {
  const bodies = new Map<string, CallBody>();
  const ordered = [...members].sort((left, right) => {
    const leftOwner = left.owner === owner ? 0 : 1;
    const rightOwner = right.owner === owner ? 0 : 1;
    return leftOwner - rightOwner;
  });
  for (const member of ordered) {
    if (member.kind !== "Operation" && member.kind !== "Property") {
      continue;
    }
    if (!member.text || isSimpleProperty(member.text)) {
      continue;
    }
    const key = memberKey(member.owner, member.name);
    const body: CallBody = {
      id: member.id,
      member: member.name,
      label: member.owner ? `${member.owner}.${member.name}` : member.name,
      text: member.text,
      types: typesIn(member.kind, member.text, classes),
    };
    if (!bodies.has(key)) {
      bodies.set(key, body);
    }
    if (!bodies.has(member.name)) {
      bodies.set(member.name, body);
    }
  }
  return bodies;
}

function bodiesByMember(bodies: Map<string, CallBody>): Map<string, CallBody> {
  const byName = new Map<string, CallBody>();
  for (const body of bodies.values()) {
    if (!byName.has(body.member)) {
      byName.set(body.member, body);
    }
  }
  return byName;
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

function displayedCallSource(
  text: string,
  bodies: Map<string, CallBody>,
  depth: number,
  stack: string[],
  known: ClassBody[],
  anchored: CallBody[],
  listClasses: boolean,
  namedCalls: CallBody[] = [],
  namedClasses: ClassBody[] = [],
  hold: Set<string> = new Set(),
  seenClasses: Set<string> = new Set(),
  inherited: Map<string, string> = new Map(),
): { text: string; folds: CallFold[]; lineNumbers: string[]; depths: number[] } {
  const bindings = new Map(inherited);
  for (const [name, typeName] of variableTypes(text)) {
    bindings.set(name, typeName);
  }
  const folds: CallFold[] = [];
  const lineNumbers: string[] = [];
  const depths: number[] = [];
  const output: string[] = [];
  const nest = Math.max(0, depth - 1);
  const frames: { at: number; openedTo: number; member: boolean }[] = [];
  let brace = 0;
  let quote = "";
  const classDecl = /^\s*(export\s+)?(abstract\s+)?class\s+/;
  text.split("\n").forEach((line, index) => {
    output.push(line);
    lineNumbers.push(String(index + 1));
    depths.push(nest);
    const sourceLine = output.length;
    const before = brace;
    const scanned = scanBraces(line, brace, quote);
    brace = scanned.depth;
    quote = scanned.quote;
    if (!classDecl.test(line)) {
      const member = isMemberHead(line);
      for (let next = before + 1; next <= brace; next += 1) {
        frames.push({ at: sourceLine, openedTo: next, member: member && next === before + 1 });
      }
    }
    if (depth < MAX_DEPTH) {
      const calls = callsOnLine(line, bodies, stack, bindings);
      if (index === 0) {
        for (const call of anchored) {
          if (!calls.some((listed) => listed.id === call.id)) {
            calls.push(call);
          }
        }
      }
      for (const call of namedCalls) {
        if (wordHas(line, call.member) && !calls.some((listed) => listed.id === call.id) && !stack.includes(call.id)) {
          calls.push(call);
        }
      }
      const fromCalls = typesOn(calls);
      const mentioned = known.filter(
        (type) =>
          !stack.includes(type.id) &&
          !fromCalls.some((listed) => listed.id === type.id) &&
          mentionsType(line, type.name),
      );
      for (const type of namedClasses) {
        if (wordHas(line, type.name) && !fromCalls.some((listed) => listed.id === type.id) && !mentioned.some((listed) => listed.id === type.id)) {
          mentioned.push(type);
        }
      }
      for (const type of typesForVariables(line, bindings, known)) {
        if (
          stack.includes(type.id) ||
          fromCalls.some((listed) => listed.id === type.id) ||
          mentioned.some((listed) => listed.id === type.id)
        ) {
          continue;
        }
        mentioned.push(type);
      }
      const listedIds = new Set([...fromCalls, ...mentioned].map((type) => type.id));
      const extras = index === 0 && listClasses ? known.filter((type) => !listedIds.has(type.id)) : [];
      const constructed = typesConstructed(line, known);
      const listedTypes = [...fromCalls, ...mentioned, ...extras, ...constructed].filter(
        (type, typeIndex, all) =>
          all.findIndex((item) => item.id === type.id) === typeIndex &&
          (!hold.has(type.id) || constructed.some((item) => item.id === type.id)),
      );
      const pad = `${indentOf(line)}    `;
      const callLine = output.length;
      const held = new Set(listedTypes.map((type) => type.id));
      for (const call of calls) {
        appendOperation(output, lineNumbers, depths, folds, call, bodies, depth, stack, pad, known, held, seenClasses);
      }
      for (const type of listedTypes) {
        appendClass(
          output,
          lineNumbers,
          depths,
          folds,
          type,
          pad,
          stack,
          depth,
          seenClasses,
          constructed.some((item) => item.id === type.id),
        );
      }
      if ((calls.length > 0 || listedTypes.length > 0) && output.length > callLine) {
        folds.push({
          start: callLine,
          end: output.length,
          kind: calls.length > 0 ? "call" : "class",
          listed: calls.length === 0,
        });
      }
    }
    while (frames.length > 0 && brace < frames[frames.length - 1].openedTo) {
      const frame = frames.pop();
      if (!frame || output.length <= frame.at) {
        continue;
      }
      const listed = folds.some(
        (fold) => fold.start === frame.at && (fold.kind === "call" || fold.kind === "class"),
      );
      if (listed) {
        continue;
      }
      folds.push({ start: frame.at, end: output.length, kind: "block", member: frame.member });
    }
  });
  return { text: output.join("\n"), folds, lineNumbers, depths };
}

function wordHas(line: string, name: string): boolean {
  return new RegExp(`\\b${name}\\b`).test(line);
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

function typesForVariables(line: string, bindings: Map<string, string>, known: ClassBody[]): ClassBody[] {
  const code = line.replace(/'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`/g, " ");
  const found: ClassBody[] = [];
  const seen = new Set<string>();
  for (const [variable, typeName] of bindings) {
    if (!wordHas(code, variable)) {
      continue;
    }
    const type = known.find((item) => item.name === typeName);
    if (!type || seen.has(type.id) || SKIP_TYPES.has(type.name)) {
      continue;
    }
    seen.add(type.id);
    found.push(type);
  }
  return found;
}

function callsOnLine(
  line: string,
  bodies: Map<string, CallBody>,
  stack: string[],
  bindings: Map<string, string>,
): CallBody[] {
  const found: CallBody[] = [];
  const seen = new Set<string>();
  const add = (body: CallBody | undefined) => {
    if (!body || stack.includes(body.id) || seen.has(body.id) || isSimpleProperty(body.text)) {
      return;
    }
    seen.add(body.id);
    found.push(body);
  };
  const pattern = /\b([A-Za-z_][A-Za-z0-9_]*)\??\.([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(line))) {
    if (!SKIP_TYPES.has(match[1])) {
      add(resolveCall(bodies, match[1], match[2], bindings.get(match[1])));
    }
    const next = match.index + match[1].length + (match[0].includes("?.") ? 2 : 1);
    if (pattern.lastIndex > next) {
      pattern.lastIndex = next;
    }
  }
  return found;
}

function resolveCall(
  bodies: Map<string, CallBody>,
  receiver: string,
  method: string,
  typeName?: string,
): CallBody | undefined {
  if (typeName) {
    const typed = bodies.get(`${typeName}.${method}`);
    if (typed) {
      return typed;
    }
  }
  if (receiver !== "this") {
    const exact = bodies.get(`${receiver}.${method}`);
    if (exact) {
      return exact;
    }
    const wanted = receiver.toLowerCase();
    for (const [key, body] of bodies) {
      const dot = key.lastIndexOf(".");
      if (dot < 0 || key.slice(dot + 1) !== method) {
        continue;
      }
      if (key.slice(0, dot).toLowerCase() === wanted) {
        return body;
      }
    }
  }
  return bodies.get(method);
}

function appendOperation(
  output: string[],
  lineNumbers: string[],
  depths: number[],
  folds: CallFold[],
  call: CallBody,
  bodies: Map<string, CallBody>,
  depth: number,
  stack: string[],
  pad: string,
  known: ClassBody[],
  hold: Set<string>,
  seenClasses: Set<string>,
) {
  output.push(`${pad}${call.member}`);
  lineNumbers.push("");
  depths.push(depth);
  const operationLine = output.length;
  const nested = displayedCallSource(
    call.text,
    bodies,
    depth + 1,
    [...stack, call.id],
    known,
    [],
    false,
    [],
    [],
    hold,
    seenClasses,
  );
  const bodyPad = `${pad}    `;
  for (const [index, nestedLine] of nested.text.split("\n").entries()) {
    output.push(nestedLine.length > 0 ? `${bodyPad}${nestedLine}` : bodyPad);
    lineNumbers.push("");
    depths.push((nested.depths[index] ?? depth) + 1);
  }
  if (output.length > operationLine) {
    folds.push({ start: operationLine, end: output.length, kind: "call" });
  }
  for (const fold of nested.folds) {
    if (fold.start === 1 && fold.kind === "block") {
      continue;
    }
    folds.push({
      start: operationLine + fold.start,
      end: operationLine + fold.end,
      kind: fold.kind,
      member: fold.member,
      listed: fold.listed,
    });
  }
}

function appendClass(
  output: string[],
  lineNumbers: string[],
  depths: number[],
  folds: CallFold[],
  type: ClassBody,
  pad: string,
  stack: string[],
  depth: number,
  seenClasses: Set<string>,
  again = false,
) {
  if (stack.includes(type.id) || (seenClasses.has(type.id) && !again)) {
    return;
  }
  seenClasses.add(type.id);
  output.push(`${pad}${type.name}`);
  lineNumbers.push("");
  depths.push(depth);
  const classLine = output.length;
  const classLines = type.text.split("\n");
  if (classLines.length === 0 || (classLines.length === 1 && classLines[0].trim() === type.name)) {
    return;
  }
  const classPad = `${pad}    `;
  for (const classLineText of classLines) {
    output.push(classLineText.length > 0 ? `${classPad}${classLineText}` : classPad);
    lineNumbers.push("");
    depths.push(depth + 1);
  }
  folds.push({ start: classLine, end: output.length, kind: "class", listed: true });
  for (const brace of braceFolds(type.text)) {
    folds.push({
      start: classLine + brace.glyph,
      end: classLine + brace.end,
      kind: "block",
      member: brace.member,
    });
  }
}

function typesConstructed(line: string, known: ClassBody[]): ClassBody[] {
  const code = line.replace(/'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`/g, " ");
  const found: ClassBody[] = [];
  const seen = new Set<string>();
  for (const match of code.matchAll(/\bnew\s+([A-Za-z_][A-Za-z0-9_]*)\b/g)) {
    const type = known.find((item) => item.name === match[1]);
    if (!type || seen.has(type.id) || SKIP_TYPES.has(type.name)) {
      continue;
    }
    seen.add(type.id);
    found.push(type);
  }
  return found;
}

function mentionsType(line: string, name: string): boolean {
  if (SKIP_TYPES.has(name)) {
    return false;
  }
  const code = line.replace(/'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`/g, " ");
  return new RegExp(`\\b${name}\\b`).test(code);
}

function typesOn(calls: CallBody[]): ClassBody[] {
  const types: ClassBody[] = [];
  const seen = new Set<string>();
  for (const call of calls) {
    for (const type of call.types) {
      if (seen.has(type.id)) {
        continue;
      }
      seen.add(type.id);
      types.push(type);
    }
  }
  return types;
}

function indentOf(line: string): string {
  return line.match(/^\s*/)?.[0] ?? "";
}
