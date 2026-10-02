import { resolveNamedFolder } from '../../packages/explore-knowledge-graph/knowledge-graph/workspace';

describe('resolveNamedFolder', () => {
  const dirs = new Set([
    'C:/dev/abd-context-driven-delivery',
    'C:/dev',
    'C:/dev/paradise-mobile',
    'C:/dev/paradise-mobile/pml-web',
  ]);
  const children: Record<string, string[]> = {
    'C:/dev': ['abd-context-driven-delivery', 'paradise-mobile'],
    'C:/dev/paradise-mobile': ['pml-web'],
  };
  const isDir = (path: string) => dirs.has(path.replaceAll('\\', '/'));
  const childrenOf = (path: string) => children[path.replaceAll('\\', '/')] ?? [];
  const joinPath = (...parts: string[]) => parts.join('/');
  const baseName = (path: string) => path.split('/').at(-1) ?? '';

  it('finds a sibling-of-sibling repo from the last folder name only', () => {
    const found = resolveNamedFolder(
      'pml-web',
      ['C:/dev/abd-context-driven-delivery', 'C:/dev'],
      isDir,
      childrenOf,
      joinPath,
      baseName,
    );
    expect(found).toBe('C:/dev/paradise-mobile/pml-web');
  });
});
