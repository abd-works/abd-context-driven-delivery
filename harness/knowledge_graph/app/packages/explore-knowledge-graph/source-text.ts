import type { ListedTreeNode, SourceRangeDto } from './knowledge-graph/knowledge-graph';

export function sourceKey(range: { file: string; start_line: number; end_line: number }): string {
  return `${range.file}:${range.start_line}:${range.end_line}`;
}

export function sourcesMissingText(node: ListedTreeNode | null | undefined): SourceRangeDto[] {
  const found: SourceRangeDto[] = [];
  const seen = new Set<string>();
  const visit = (current: ListedTreeNode | null | undefined) => {
    if (!current) {
      return;
    }
    for (const source of [current.source, current.origin]) {
      if (!source?.file || source.text) {
        continue;
      }
      const key = sourceKey(source);
      if (seen.has(key)) {
        continue;
      }
      seen.add(key);
      found.push(source);
    }
    for (const child of current.children ?? []) {
      visit(child);
    }
  };
  visit(node);
  return found;
}

export function withSourceText(node: ListedTreeNode, texts: Map<string, string>): ListedTreeNode {
  const fill = (source: SourceRangeDto | null): SourceRangeDto | null => {
    if (!source?.file || source.text) {
      return source;
    }
    const text = texts.get(sourceKey(source));
    return text ? { ...source, text } : source;
  };
  return {
    ...node,
    source: fill(node.source),
    origin: fill(node.origin),
    children: (node.children ?? []).map((child) => withSourceText(child, texts)),
  };
}
