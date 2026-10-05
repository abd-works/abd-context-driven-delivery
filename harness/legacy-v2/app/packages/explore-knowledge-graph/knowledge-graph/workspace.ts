export function pickerRelativePath(webkitRelativePath: string): {
  folder: string;
  relativePath: string;
} {
  const normalized = webkitRelativePath.replaceAll('\\', '/');
  const slash = normalized.indexOf('/');
  if (slash < 0) {
    return { folder: 'workspace', relativePath: normalized };
  }
  return {
    folder: normalized.slice(0, slash),
    relativePath: normalized.slice(slash + 1),
  };
}

/** Native pickers only give the last folder name, not a disk path. */
export function resolveNamedFolder(
  chosen: string,
  bases: string[],
  isDir: (path: string) => boolean,
  childrenOf: (path: string) => string[],
  joinPath: (...parts: string[]) => string,
  baseName: (path: string) => string,
): string | undefined {
  const name = chosen.trim();
  if (!name) {
    return undefined;
  }
  if (isDir(name)) {
    return name;
  }
  const key = compactFolderName(name);
  for (const base of bases) {
    if (!base) {
      continue;
    }
    if (sameFolderName(baseName(base), name) && isDir(base)) {
      return base;
    }
    const nested = joinPath(base, name);
    if (isDir(nested)) {
      return nested;
    }
    if (!isDir(base)) {
      continue;
    }
    for (const child of childrenOf(base)) {
      const childPath = joinPath(base, child);
      if (sameFolderName(child, name) && isDir(childPath)) {
        return childPath;
      }
      const deeper = joinPath(base, child, name);
      if (isDir(deeper)) {
        return deeper;
      }
      if (!isDir(childPath)) {
        continue;
      }
      for (const grandchild of childrenOf(childPath)) {
        if (!sameFolderName(grandchild, name)) {
          continue;
        }
        const match = joinPath(childPath, grandchild);
        if (isDir(match)) {
          return match;
        }
      }
    }
    if (key && sameFolderName(baseName(base), key) && isDir(base)) {
      return base;
    }
  }
  return undefined;
}

function compactFolderName(name: string): string {
  return name.trim().toLowerCase().replace(/[\s_-]+/g, '');
}

function sameFolderName(left: string, right: string): boolean {
  return left === right || compactFolderName(left) === compactFolderName(right);
}
