export type ViolationFocus = {
  rule: string;
  message: string;
  startLine?: number;
  endLine?: number;
};

export function buildViolationCorrectPrompt(input: {
  rule: string;
  message: string;
  nodeName: string;
  nodeType: string;
  file: string;
  startLine: number;
  endLine: number;
  excerpt: string;
}): string {
  const fileSpan = input.startLine >= 1 ? `${input.file}:${input.startLine}-${input.endLine}` : input.file;
  return [
    'Fix this violation using the Clean Engineering practice guidelines and a test-driven approach.',
    'Run or add tests that express the intended behavior before or alongside the fix.',
    '',
    `Node: ${input.nodeName} (${input.nodeType})`,
    fileSpan ? `File: ${fileSpan}` : '',
    `Rule: ${input.rule}`,
    '',
    'Erroneous code:',
    '```',
    input.excerpt,
    '```',
    '',
    `Violation: ${input.message}`,
  ].join('\n');
}
